import random
import urllib.request

from grader_app.models import *

word_url = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
response = urllib.request.urlopen(word_url)
long_txt = response.read().decode()
words = long_txt.splitlines()
for _ in range(100):
    words.append(".")

upper_words = [word for word in words if word[0].isupper()]
name_words = [word for word in upper_words if not word.isupper()]
for n in range(1000):
    user = User.objects.get(email="2023pbhandar@tjhsst.edu")
    body = ' '.join([random.choice(words) for i in range(1000)])
    essay = Essay(author=user, teacher=User.objects.get(email="2023pbhandar@tjhsst.edu"), title=random.choice(words),
                  body=body, citation_type="APA", assignment=Assignment.objects.get(assignment_name="Hello"))
    essay.save()
