import re
import os
import urllib2
import urlparse
from optparse import OptionParser

def main():
  parser = OptionParser(usage = "usage = %prog OPTIONS domain url")
  parser.add_option("--out", dest = "out")
  (options, args) = parser.parse_args()

  if len(args) < 2:
    print "Incorrect arguments"
    parser.print_help()
    exit(1)

  directory = options.out or os.getcwd()
  first = args[1]
  domain = args[0]
  processed = []
  queue = [ first ]
  count = 0

  if not os.path.isdir(directory):
    os.makedirs(directory)

  if not domain in queue[0]:
    print "Provided domain not found in start URL"
    parser.print_help()
    exit(1)

  print "saving in {}".format(directory)
  print "using domain {}".format(domain)
  print "start URL {}".format(queue[0])

  while len(queue) > 0:
    url = queue.pop()

    if url in processed:
      continue

    parsed = urlparse.urlparse(url)

    if domain not in parsed.netloc and not is_relative_url(url):
      processed.append(url)
      continue

    print "scraping {}".format(url)
    (urls, data, is_html) = scrape_next(url, first)

    if data is None:
      processed.append(url)
      continue

    if is_html:
      queue.extend([s for s in urls if (domain in s or is_relative_url(s) and \
                                        s not in queue and s not in processed)])

    write_local_data(directory, parsed, data, is_html)
    processed.append(url)
    count += 1

  print "done -- processed {} urls".format(count)
  exit(0)

def is_relative_url(url):
  return re.match(r'^\w+://', url) is None

def write_local_data(directory, parsed_url, data, is_html):
  path = os.path.abspath(directory + parsed_url.path + parsed_url.query)

  if not path.endswith('.html') and is_html:
    if not path.endswith(os.sep):
      path += os.sep
    path += 'index.html'

  directory = os.path.dirname(path)
  if not directory.endswith(os.sep):
    directory += os.sep
  if not os.path.isdir(directory):
    os.makedirs(directory)

  with open(path, 'wb') as f:
    f.write(data)

def scrape_next(url, url_base):
  urls = []
  url = urlparse.urljoin(url_base, url)

  try:
    response = urllib2.urlopen(url)
  except urllib2.HTTPError as e:
    print "http error {} reading {}: {}".format(e.code, url, e.reason)
    return (None, None, None)
  except urllib2.URLError as e:
    print "bad url {}: {}".format(url, e.reason)
    return (None, None, None)
  except:
    print "unexpected error reading {}".format(url)
    return (None, None, None)

  data = response.read()
  is_html = response.info().getsubtype() == "html"
  response.close()

  if is_html:
    urls = re.findall(r'(?:href|src)=[\'"]?([^\'" >]+)', data)

  return (urls, data, is_html)

if __name__ == "__main__":
    main()
