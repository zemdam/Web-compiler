# About

Simple web app for compiling C code made for Web applications course at MIMUW.
<details>
<summary>Screenshots</summary>

![First](https://i.imgur.com/ckVjpbf.png)
![Second](https://i.imgur.com/WLbeQAH.png)

</details>

# Requirements and initial account

To install and use app you need:

- python
- sdcc

You can login using:

- login: admin
- password: admin

# How to run for development

0. Create python env.

```
python3 -m venv env
```

1. Switch to created python env.

```
source env/bin/activate
```

2. Install needed packages:

```
pip install -r requirements.txt
```

3. Run server via:

```
python3 manage.py runserver
```
4. App is available on `127.0.0.1:8000`
# How to run with nginx

0. Install `uwsgi` and `nginx`.
1. Change `{path}` to absolute path to `web_compiler` directory in `web_compiler_nginx.conf` file.
2. Copy `web_compiler_nginx.conf` to `/etc/nginx/sites-available/`.

```
sudo cp web_compiler_nginx.conf /etc/nginx/sites-available/
```

3. Create link.

```
sudo ln -s /etc/nginx/sites-available/web_compiler_nginx.conf /etc/nginx/sites-enabled/
```

4. Change `user` in `/etc/nginx/nginx.conf` to your username. (Needed to access static folder).
5. Restart nginx.

```
sudo /etc/init.d/nginx restart
```

6. Run app via:

```
uwsgi --socket :8001 --module web_compiler.wsgi
```

7. App is available on `127.0.0.1:8000`
