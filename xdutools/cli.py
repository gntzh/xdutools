import click
from .login import Login


@click.group()
def cli():
    pass


@cli.command()
@click.option('--username', '-U', 'username', prompt='账号')
@click.option('--password', '-P', 'password', prompt='密码')
@click.option('--format', '-f', type=click.Choice(('simple', 'csv', 'wakeup')), default='csv')
def schedule(username, password, format):
    from .schedule import Lesson, APP_NAME
    login = Login(username, password)
    login.ids_login()
    click.secho('ids登录成功', fg='green')
    login.request_app(APP_NAME)
    click.secho('我的课表访问成功', fg='green')
    lesson = Lesson()
    lessons = lesson.get_lessons(login.session)
    click.secho('成功获得课表', fg='green')
    lesson.save_lessons(lessons, format)
