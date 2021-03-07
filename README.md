# GitRekt

GitRekt is a tool that can be used to scrape a websites .git folder. By default GitRekt will search for email addresses and URL's that should otherwise be hidden. The .git folder is a very useful thing when running recon on a website, now you can do it automatically. Enjoy!

# Examples

```
python gitrekt.py -u http://startupxxxxxx.fi
          ________.__  __ __________        __      __
         /  _____/|__|/  |\______   \ ____ |  | ___/  |_
        /   \  ___|  \   __\       _// __ \|  |/ /\   __\
        \    \_\  \  ||  | |    |   \  ___/|    <  |  |
         \______  /__||__| |____|_  /\___  >__|_ \ |__|
                \/                \/     \/     \/    v0.1
starting request on url: http://http://startupxxxxxx.fi.fi
not using a proxy
searching for interesting data in .git folder
cleaning found data
saving to file
results written to: /fake/path/results/startupxxxxxx.fi
found a total of 2 email(s) and 98 url(s)
```