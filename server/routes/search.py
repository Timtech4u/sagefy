from framework.routes import get
from framework.elasticsearch import es


@get('/s/search')
def search_route(request):
    """
    Search for entities: user, card, unit, set, topic, and post.
    Search, filter, sort, paginate.

    Parameters:
    - q: query string
    - skip: for pagination
    - limit: for pagination
    - order: created...
    - kind: the kind of entity to search for (e.g. set, card, unit)
    """

    # elasticsearch doc: http://bit.ly/1NdvIoi
    result = es.search(
        index="entity",
        doc_type=request['params'].get('kind') or
        "user,card,unit,set,topic,post",
        q=request['params'].get('q'),
        size=request['params'].get('limit') or 10,
        from_=request['params'].get('skip') or 0,
        # TODO-2 sort=request['params'].get('order') or 'score:desc',
    )

    return 200, result['hits']
