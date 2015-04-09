from framework.session import get_current_user
from framework.routes import get, post, abort
from models.card import Card
from models.unit import Unit
from models.topic import Topic
from modules.entity import get_card_by_kind
from modules.sequencer.index import update as seq_update


@get('/api/cards/{card_id}')
def get_card_route(request, card_id):
    """
    Get a specific card given an ID. Show all relevant data, but
    not used for the learning interface.
    """

    card = get_card_by_kind(card_id)
    if not card:
        return abort(404)

    unit = Unit.get_latest_canonical(entity_id=card['unit_id'])
    if not unit:
        return abort(404)

    topics = Topic.list_by_entity_id(entity_id=card_id)
    versions = Card.get_versions(entity_id=card_id)
    requires = Card.list_requires(entity_id=card_id)
    required_by = Card.list_required_by(entity_id=card_id)

    return 200, {
        'card': card.deliver(access='view'),
        'unit': unit.deliver(),
        'topics': [topic.deliver() for topic in topics],
        'versions': [version.deliver() for version in versions],
        'requires': [require.deliver() for require in requires],
        'required_by': [require.deliver() for require in required_by],
    }

    # TODO@ sequencer data: learners, transit, guess, slip, difficulty


@get('/api/cards/{card_id}/versions')
def get_card_versions_route(request, card_id):
    """
    Get versions card given an ID. Paginates.
    """

    # TODO@ add pagination
    versions = Card.get_versions(entity_id=card_id)
    return 200, {
        'versions': [version.deliver(access='view') for version in versions]
    }


@get('/api/cards/{card_id}/learn')
def learn_card_route(request, card_id):
    """
    Render the card's data, ready for learning.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)

    card = get_card_by_kind(card_id)
    if not card:
        return abort(404)

    context = current_user.get_learning_context()
    if context.get('unit', {}).get('id') != card['unit_id']:
        return abort(400)

    current_user.set_learning_context(card=card)

    return 200, {
        'card': card.deliver(access=''),
        'set': context.get('set'),
        'unit': context.get('unit')
    }


@post('/api/cards/{card_id}/responses')
def respond_to_card_route(request, card_id):
    """
    Record and process a learner's response to a card.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)

    card = get_card_by_kind(card_id)
    if not card:
        return abort(404)

    context = current_user.get_learning_context()
    if (context.get('card', {}).get('id') != card['entity_id'] or
            context.get('unit', {}).get('id') != card['unit_id']):
        return abort(400)

    current_user.set_learning_context(card=None)

    r = seq_update(current_user, card, request['params'].get('response'))
    errors, response, feedback = (r.get('errors'), r.get('response'),
                                  r.get('feedback'))
    if errors:
        return 400, {'errors': errors}

    return 200, {
        'response': response.deliver(),
        'feedback': feedback
    }
