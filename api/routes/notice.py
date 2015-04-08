from framework.routes import get, put, abort
from framework.session import get_current_user
from models.notice import Notice


def add_body_to_notices(notices):
    parsed = []
    for notice in notices:
        n = notice.deliver(access='private')
        n['body'] = notice.get_body()
        parsed.append(n)
    return parsed


@get('/api/notices')
def list_notices_route(request):
    """
    List notices for current user.
    Take parameters `limit`, `skip`, `tag`, and `read`.
    """

    current_user = get_current_user()
    if not current_user:
        return abort(401)
    notices = Notice.list(user_id=current_user['id'], **request['params'])
    return 200, {'notices': add_body_to_notices(notices)}


# TODO Dry up the mark as read/unread routes


@put('/api/notices/{notice_id}/read')
def mark_notice_as_read_route(request, notice_id):
    """
    Mark notice as read.
    Must be logged in as user, provide a valid ID, and own the notice.
    Return notice.
    """

    current_user = get_current_user()
    if not current_user:
        return abort(401)
    notice = Notice.get(id=notice_id)
    if not notice:
        return abort(404)
    if notice['user_id'] != current_user['id']:
        return abort(403)
    notice, errors = notice.mark_as_read()
    if len(errors):
        return 400, {'errors': errors}
    return 200, {'notice': notice.deliver(access='private')}


@put('/api/notices/{notice_id}/unread')
def mark_notice_as_unread_route(request, notice_id):
    """
    Mark notice as unread.
    Must be logged in as user, provide a valid ID, and own the notice.
    Return notice.
    """

    current_user = get_current_user()
    if not current_user:
        return abort(401)
    notice = Notice.get(id=notice_id)
    if not notice:
        return abort(404)
    if notice['user_id'] != current_user['id']:
        return abort(403)
    notice, errors = notice.mark_as_unread()
    if len(errors):
        return 400, {'errors': errors}
    return 200, {'notice': notice.deliver(access='private')}
