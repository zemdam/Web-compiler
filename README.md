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