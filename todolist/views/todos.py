from pyramid.view import view_config

from ..models import Todo


@view_config(route_name='todo_list', renderer='../templates/todos_list.jinja2')
def todo_list(request):
    todos = request.dbsession.query(Todo).all()
    return {'todos': todos}


@view_config(route_name='todo_view', renderer='../templates/todo_view.jinja2')
def todo_view(request):
    id_ = int(request.matchdict.get('id'))
    todo = request.dbsession.query(Todo).filter(Todo.id == id_).first()
    return {'todo': todo}
