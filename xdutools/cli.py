import click
from .login import Login


@click.group()
@click.option('--username', '-U', 'username', prompt='账号')
@click.pass_context
def main(ctx, username):
    login = Login.by_cookies()
    if username != login.status:
        password = click.prompt('密码')
        login = Login(username, password)
        login.ids_login()
    login.save_cookies()
    # TODO 登录是否成功的检查并没有做
    click.secho('ids登录成功', fg='green')
    ctx.ensure_object(dict)
    ctx.obj['login'] = login


# TODO 允许选择哪一学期课表 功能
@main.command()
@click.option('--format',
              '-f',
              type=click.Choice(('simple', 'csv', 'wakeup')),
              default='csv')
@click.pass_obj
def schedule(obj, format):
    login = obj['login']
    from .schedule import Lesson, APP_NAME
    login.request_app(APP_NAME)
    click.secho('我的课表访问成功', fg='green')
    lesson = Lesson()
    lessons = lesson.get_lessons(login.session)
    click.secho('成功获得课表', fg='green')
    lesson.save_lessons(lessons, format)
    click.secho('成功保存课表', fg='green')


@main.command()
@click.pass_obj
def score(obj):
    login = obj['login']
    from .score import APP_NAME, Score
    login.request_app(APP_NAME)
    click.secho('成绩查询访问成功', fg='green')
    lesson = Score()
    lessons = lesson.get_scores(login.session)
    click.secho('成功获得成绩', fg='green')
    lesson.save_scores(lessons)
    click.secho('成功保存成绩', fg='green')
