import re
import os

try:
    # python2
    from urlparse import urlparse
except:
    # python3
    from urllib.parse import urlparse

import requests


RESULTS_FOLDER = "{}/results".format(os.getcwd())
# paths in the .git folder you will probably want
GIT_PATHS = (
    ".git/logs/refs/remotes/origin/master",
    ".git/logs/refs/heads/master",
    ".git/COMMIT_EDITMSG",
    ".git/config",
    ".git/info/exclude",
    ".git/refs/remotes/origin/master"
)
VERSION = "0.1"
HEADER = """\t  ________.__  __ __________        __      __   
\t /  _____/|__|/  |\\______   \\ ____ |  | ___/  |_ 
\t/   \\  ___|  \\   __\\       _// __ \\|  |/ /\\   __\\
\t\\    \\_\\  \\  ||  | |    |   \\  ___/|    <  |  |  
\t \\______  /__||__| |____|_  /\\___  >__|_ \\ |__|  
\t        \\/                \\/     \\/     \\/    v{}""".format(VERSION)


def fix_repr(obj):
    """
    fixes a representation of a string to make a real string for example
    d = repr(... some item ..)
    print(d) => ' ... some stuff ... '
    print(fix_repr(d)) => ... some stuff ... # takes away the '
    """
    if obj.startswith("u"):
        fixed = obj[2:-1]
    else:
        fixed = obj[1:-1]
    return fixed


def find_interesting(data):
    """
    find emails and urls in the files and try to parse them out
    """
    found_data = {"emails": [], "urls": []}
    interesting_data = {
        "email": re.compile(r'[\w\.-]+@[\w\.-]+'),
        "url": re.compile(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)')
    }
    for regex in interesting_data.keys():
        for data_ in list(data):
            found = interesting_data[regex].findall(data_)
            for item in found:
                if isinstance(item, (list, tuple)):
                    for _item in item:
                        if len(item) != 0:
                            if regex == "email":
                                found_data["email"].append(_item)
                            else:
                                found_data["urls"].append(_item)
                else:
                    if regex == "email":
                        found_data["emails"].append(item)
                    else:
                        found_data["urls"].append(item)
    return found_data


def make_unique(searchable):
    """
    turn a jumbled mess of garbage into a unique mess of garbage
    """
    data_results = set()
    for item in searchable.keys():
        for _item in searchable[item]:
            data_results.add((item, _item))
    return data_results


def validate_url(url, parts=False):
    """
    validate if a url is good or not
    """
    try:
        results = urlparse(url)
        if parts:
            return results
        else:
            return True
    except:
        return False


def defang(item, is_email=False):
    """
    defang a url
    """
    if is_email:
        return item.replace("@", "[@]")
    else:
        return item.replace("http", "hxxp").replace(".", "[.]")


def make_pretty(data):
    """
    turn everything into a pretty dict
    """
    cleaned_results = {"emails": [], "urls": []}
    found_emails = found_urls = 0
    for result in data:
        type_found, item_found = result[0], result[1]
        if type_found == "urls":
            if validate_url(item_found):
                found_urls += 1
                cleaned_results["urls"].append(defang(item_found))
        else:
            found_emails += 1
            cleaned_results["emails"].append(defang(item_found, is_email=True))
    return cleaned_results


def make_request(url, proxy, paths):
    """
    make the request
    """
    searchable = set()
    if proxy is None:
        print("not using a proxy")
        proxy = {}
    else:
        print("using proxy: {}".format(proxy))
        proxy = {"http": proxy, "https": proxy}
    for path in paths:
        url = "{}/{}".format(url, path)
        req = requests.get(url, proxies=proxy)
        for line in req.text.split("\n"):
            try:
                to_search = line
            except:
                to_search = fix_repr(repr(line))
            searchable.add(to_search)
    return searchable


def write_to_files(results, url):
    """
    write the results to a file
    """
    netloc = validate_url(url, parts=True).netloc
    if not os.path.exists(RESULTS_FOLDER):
        os.makedirs(RESULTS_FOLDER)
    path = "{}/{}".format(RESULTS_FOLDER, netloc)
    if not os.path.exists(path):
        os.makedirs(path)
        for key in results.keys():
            results_path = "{}/{}/{}.results".format(RESULTS_FOLDER, netloc, key)
            with open(results_path, "a+") as f:
                for result in results[key]:
                    f.write(result.strip() + "\n")
        print("results written to: {}".format(path))
    else:
        print("path ({}) already exists, skipping writing".format(path))


def main(url, proxy):
    """
    main function
    """
    print("starting request on url: {}".format(url))
    results = make_request(url, proxy, GIT_PATHS)
    print("searching for interesting data in .git folder")
    interesting = find_interesting(results)
    print("cleaning found data")
    unique_data = make_unique(interesting)
    cleaned = make_pretty(unique_data)
    print("saving to file")
    write_to_files(cleaned, url)
    print("found a total of {} email(s) and {} url(s)".format(len(cleaned["emails"]), len(cleaned["urls"])))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Pass a url to scan", default=None, dest="urlToScan")
    parser.add_argument("-p", "--proxy", help="Pass a proxy to use", default=None, dest="proxyToUse")
    opts = parser.parse_args()

    if opts.urlToScan is None:
        print("must supply a URL with the `-u` flag")
        exit(1)

    print(HEADER)

    main(opts.urlToScan, opts.proxyToUse)