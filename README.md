## Hello Blog by Django

### Features
* 支持Markdown格式发布文章
* 支持代码高亮
* 支持普通用户注册和登录
* 支持注册成功发送邮件通知
* 支持普通用户在线编辑、删除文章
* 支持修改用户头像
* 支持全文搜索
* 支持分类和标签筛选文章
* 支持多说评论

### Usage
一般情况下，我们都会创建一个虚拟环境去开发一个新项目，你可以选择 virtualenv 或者 pyenv，至于如何安装使用，请自行Google。配置好开发环境之后，就执行下面的命令：

```bash
$ git clone https://github.com/LooEv/Hello-Blog-by-Django.git
$ cd Hello-Blog-by-Django
$ pip install -r requirements.txt
$ python manage.py makemigrations
$ python magage.py migrate
$ python magage.py collectstatic
$ python manage.py runserver 127.0.0.1:8001
```
### Warning
需要适当修改 settings.py 文件才能成功运行这个项目，请注意。


博客系统正在不断更新中...

网站部署在[pythonanywhere](http://pythonanywhere.com/)上面，这是网站链接[http://fromlooq.pythonanywhere.com/](http://fromlooq.pythonanywhere.com/)