"""
Routes for the discussion platform.
Includes topics, posts, proposals, votes, and flags.
"""

from flask import Blueprint, abort, jsonify, request
from models.topic import Topic
from flask.ext.login import current_user
from modules.util import parse_args
from modules.discuss import instance_post_facade, create_post_facade


topic = Blueprint('topic', __name__, url_prefix='/api/topics')


@topic.route('/', methods=['POST'])
def create_topic():
    """
    Create a new topic. The first post (proposal, flag) must be provided.
    Flag: if a flag for the same reason exists for the entity,
        create a vote there instead.
    """

    if not current_user.is_authenticated():
        return abort(401)

    if 'topic' not in request.json:
        return jsonify(errors=[{
            'name': 'topic'
        }]), 400

    if 'post' not in request.json:
        return jsonify(errors=[{
            'name': 'post'
        }]), 400

    # Let's create the topic, but not save it until we know we
    # have a valid post
    topic_data = dict(**request.json['topic'])
    topic_data['user_id'] = current_user.get_id()
    topic = Topic(topic_data)
    post_data = dict(**request.json['post'])
    post_data['user_id'] = current_user.get_id()
    post_data['topic_id'] = topic['id']
    post = instance_post_facade(post_data)

    errors, errors2 = topic.validate(), post.validate()
    if len(errors + errors2):
        return jsonify(errors=errors + errors2), 400

    post, errors = post.save()
    topic, errors2 = topic.save()
    if len(errors + errors2):
        return jsonify(errors=errors + errors2), 400

    return jsonify(topic=topic.deliver(), post=post.deliver())


@topic.route('/<topic_id>/', methods=['PUT', 'PATCH'])
def update_topic(topic_id):
    """
    Update the topic. Only the name can be changed. Only by original author.
    """

    if not current_user.is_authenticated():
        return abort(401)

    # TODO Must be a valid topic_id

    # TODO Request must only be for name

    # TODO Must be logged in as topic's author

    # TODO Update and notify user


@topic.route('/<topic_id>/posts/', methods=['GET'])
def get_posts(topic_id):
    """
    Get a reverse chronological listing of posts for given topic.
    Includes topic meta data and posts (proposals, votes, flags).
    Paginates.
    """

    args = parse_args(request.args)

    # TODO Is the topic valid?

    # TODO Pull all kinds of posts

    # TODO For proposals, pull up the proposal entity version

    # TODO ...then pull up the proposal latest canonical version

    # TODO ...if the proposal isn't based off the latest canonical,
    #       it's invalid

    # TODO Make a diff between the latest canonical
    #       ... and the proposal entity version

    # TODO Return all data to user


@topic.route('/<topic_id>/posts/', methods=['POST'])
def create_post(topic_id):
    """
    Create a new post on a given topic.
    Accounts for posts, proposals, votes, and flags.
    Proposal: must include entity (card, unit, set) information.
    Vote: must refer to a proposal.
    """

    if not current_user.is_authenticated():
        return abort(401)

    # TODO For proposal or flag, entity must be included and valid
    kind = request.json.get('kind')
    if kind in ('proposal', 'flag',):
        pass

    # TODO For vote, must refer to a valid proposal
    if kind == 'vote':
        pass

    # The topic must be valid
    topic = Topic.get(id=request.json.get('topic_id'))
    if not request.json.get('topic_id') or not topic:
        return jsonify(errors=[{
            'name': 'topic_id',
            'message': 'Cannot find topic.',
        }]), 404

    # Try to save the post (and others)
    post_data = dict(**request.json)
    post_data['user_id'] = current_user.get_id()
    post, errors = create_post_facade(post_data)
    if len(errors):
        return jsonify(errors=errors), 400

    # TODO If a proposal has sufficient votes, move it to canonical
    #      ... and close out any prior versions dependent
    if kind == 'vote':
        pass

    return jsonify(post=post.deliver())


@topic.route('/<topic_id>/posts/<post_id>/', methods=['PUT', 'PATCH'])
def update_post(topic_id, post_id):
    """
    Update an existing post. Must be one's own post.

    For proposals:
    The only field that can be updated is the status;
    the status can only be changed to declined, and only when
    the current status is pending or blocked.
    """

    if not current_user.is_authenticated():
        return abort(401)

    # TODO Must be user's own post

    # TODO If proposal, make sure its allowed changes

    # TODO Attempt to update

    # TODO If errors, report

    # TODO Notify user of success
