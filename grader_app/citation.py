import re
from http.client import HTTPConnection, HTTPSConnection
from urllib.request import urlopen as url
from enum import Enum
from urlextract import URLExtract

# TODO: add url checking functionality
# https://github.com/eventlet/eventlet/issues/526

class APACitationStatus(str, Enum):
    AUTHOR = "author"
    YEAR = "year"
    TITLE = "title"
    JOURNAL = "journal"
    VOLUME = "volume number"
    ISSUE = "issue number"
    PAGES = "page number"
    URL = "url"


class APACitation():
    def __init__(self):
        self.authors = []
        self.year = ""
        self.title = ""
        self.journal = ""
        self.volume = ""
        self.issue = ""
        self.pages = []
        self.url = ""
        self.citation_status = APACitationStatus.AUTHOR
        self.warnings = []

    def __str__(self):
        return "Author(s): " + str(self.authors) + "\n" + \
            "Year: " + self.year + "\n" + \
            "Title: " + self.title + "\n" + \
            "Journal Title: " + self.journal + "\n" + \
            "Volume Number: " + self.volume + "\n" + \
            "Issue Number: " + self.issue + "\n" + \
            "Page Numbers (start, end): " + str(self.pages) + "\n" + \
            "URL/DOI: " + self.url + "\n" + \
            "Warnings: " + str(self.warnings) + "\n"

    def get_warnings(self):
        return "; ".join(self.warnings)
    
    def check_citation(self, citation): #NOTE: when implementing, wrap the method in a try catch and print out any error + the citation status
        cursor = 0
        ellipses = [' ... ', ' . . . ', ' … ']

        while True:
            ascii_value = ord(citation[cursor])

            # check if the current character is not " &-'." or any alphanumeric in English or Latin-1

            if ascii_value == 32 or 38 <= ascii_value <= 39 or 44 <= ascii_value <= 46 or 65 <= ascii_value <= 90 or 97 <= ascii_value <= 122 or 192 <= ascii_value <= 255 or ascii_value == 8230:
                cursor += 1
            else:
                break
                # RIGHT NOW CURSOR SHOULD EQUAL TO "(", IF IT DOESNT MARK ERROR

        if citation[cursor] != "(":
            raise Exception("Bad formatting in the author section (unknown error).")

        author_section = ""
        if citation[cursor - 1] == " ":
            author_section = citation[:cursor - 1]
        else:
            raise Exception("Bad formatting in the author section: '" + author_section + "'")
        
        # single author case
        # get rid of any non-English alphabetic characters (vowels w/ accents, etc.)
        filtered_authors = ""

        for i in author_section:
            if(192 <= ord(i) <= 222):
                filtered_authors += 'X'
            elif(223 <= ord(i) <= 255):
                filtered_authors += 'x'
            else:
                filtered_authors += i

        # check for single author
        if re.match("^[A-Z][A-Za-z-']+[,][ ][A-Z][.]$", filtered_authors) is not None \
            or re.match("^[A-Z][A-Za-z-']+[.]$", filtered_authors) is not None \
            or re.match("^[a-z]['][A-Z][a-z]+[,][ ][A-Z][.][ ][A-Z][.]$", filtered_authors) is not None \
            or re.match("^[a-z]['][A-Z][a-z]+[,][ ][A-Z][.]$", filtered_authors) is not None \
            or re.match("^[A-Z][A-Za-z-']+[,][ ][A-Z][.][ ][A-Z][.]$", filtered_authors) is not None \
            or re.match("^[A-Z][A-Za-z-']+[,][ ][A-Z][.][-][A-Z][.]$", filtered_authors) is not None:
            if ", " in filtered_authors:
                self.authors.append(author_section.split(", ")[0])
            else:
                self.authors.append(author_section[:-1])

        else:
            if " " in filtered_authors and filtered_authors[-1] == ".":
                tokens = filtered_authors[:-1].split(" ")
                for token in tokens:
                    if not re.match("^[A-Z][A-Za-z-']+$", token):
                        break
                else:
                    self.authors.append(filtered_authors)

            if self.authors == []:
                # one author with multiple parts in name
                try:
                    name = filtered_authors.split(", ")
                    if len(name) == 2:
                        lastName = name[0].split(" ")
                        for i in lastName:
                            if not re.match('^[a-z]+$') and not re.match('^[A-Z][a-z]+$'):
                                break
                        else:
                            firstName = name[1]
                            if re.match("^[A-Z][.][ ][A-Z][.]$", firstName) is not None \
                                    or re.match("^[A-Z][.][-][A-Z][.]$", firstName) is not None \
                                    or re.match("^[A-Z][.]$", firstName) is not None:
                                self.authors.append(name[0])
                except:
                    pass

            # check for multiple authors
            if self.authors == []:
                delimiters = [' & ', ' ... ', ' . . . ', ' … ']
                delim = ""

                for i in delimiters:
                    if i in author_section:
                        delim = i
                        break
                else:
                    raise Exception("Wrong formatting before last author (last author should be preceded by a '&' or ellipsis).")

                author_section = author_section.replace(delim, " ", 1)

                if ", " not in author_section:
                    raise Exception("Bad formatting in the author section: '" + author_section + "'")

                authors = author_section.split(", ")

                for i in range(len(authors)):
                    author = authors[i]

                    # last name case
                    if i % 2 == 0:
                        for ch in author:
                            if not (ord(ch) == 32 or ord(ch) == 39 or ord(ch) == 45 or 65 <= ord(ch) <= 90 or 97 <= ord(ch) <= 122 or 192 <= ord(ch) <= 255):
                                raise Exception("Bad formatting in the author section: '" + author + "'")
                        else:
                            self.authors.append(author)
                    else:
                        # get rid of all Latin-1 characters in author first name
                        filtered_author = ""

                        for ch in author:
                            if (192 <= ord(ch) <= 255):
                                filtered_author += 'X'
                            elif not (ord(ch) == 32 or 45 <= ord(ch) <= 46 or 65 <= ord(ch) <= 90):
                                raise Exception("Bad formatting in the author section: '" + filtered_author + "'")
                            else:
                                filtered_author += ch

                        if not re.match("^[A-Z][.]$", filtered_author) \
                                and not re.match("^[A-Z][.][ ][A-Z][.]$", filtered_author) \
                                and not re.match("^[A-Z][.][-][A-Z][.]$", filtered_author):
                            raise Exception("Bad formatting in an author's initials: '" + filtered_author + "'")

        if len(self.authors) > 20:
            raise Exception("Too many authors listed (there should be a maximum of 20 authors).")
        
        for i in ellipses:
            if i in citation and len(authors) != 20:
                raise Exception("In APA 7, you must list the first 19 authors and then use the ellipsis before the last author.")

            # check the year section
        self.citation_status = APACitationStatus.YEAR

        if '. (' not in citation:
            raise Exception("Error in citation formatting: the year number must be directly preceded by a period, a space, and an open parenthesis, but this was not found.")

        # move cursor to the first number in the year
        cursor += 1
        year = ""

        while citation[cursor].isalnum():
            year += citation[cursor]
            cursor += 1

        if not re.match("^[0-9]{4}$", year) and not re.match("^[0-9]{4}[a-z]$", year):
            raise Exception("Bad formatting in the year section: '" + year + "'")

        self.year = year

        if citation[cursor] == ",":
            while citation[cursor] != ")":
                cursor += 1

        if ". <i>" not in citation[cursor + 4:] and ".<i>" not in citation[cursor + 4:]:
            raise Exception("The journal title should be italicized.")

        # check title
        self.citation_status = APACitationStatus.TITLE

        cursor += 1

        if citation[cursor + 1: cursor + 4] == "<i>":
            cursor += 4
        elif citation[cursor + 2: cursor + 5] == "<i>":
            cursor += 5
        else:
            cursor += 2

        if not citation[cursor].isupper():
            raise Exception("The first word in the title should be capitalized.")

        title = ""

        while citation[cursor: cursor + 5] != ". <i>" and citation[cursor: cursor + 4] != ".<i>":
            title += citation[cursor]
            cursor += 1

        title = title.replace("<i>", "")
        title = title.replace("</i>", "")

        words = title.split(" ")

        # TODO: implement truecasing
        title_caps = []
        title_warning = ""

        for word in words[1:]:
            if word[0].isalpha() and word[0].isupper():
                title_caps.append(word)
        
        if title_caps != []:
            title_warning += "the following words are capitalized in the title: "
            for cap in title_caps:
                title_warning += cap + ", "

        self.warnings.append(title_warning[:-2])

        cursor += 1

        self.title = " ".join(words)

        # check journal name
        self.citation_status = APACitationStatus.JOURNAL

        journal = ""
        while citation[cursor: cursor + 2] != ", " and citation[cursor: cursor + 4] != ",<i>":
            journal += citation[cursor]
            cursor += 1

        if journal[-4:] == "</i>":
            journal = journal[:-4]
            
        if "<i>" not in journal or "</i>" in journal:
            raise Exception("The journal title should be italicized.")

        journal = journal.replace("<i>", "")

        self.journal = journal
        
        if citation[cursor + 1 : cursor + 4] == "<i>":
            citation = citation[:cursor + 1] + " " + citation[cursor + 1 : cursor + 4] + citation[cursor + 5:]
            
        if citation[cursor : cursor + 2] != ", ":
            raise Exception("There should be a comma and a space after the journal title, and the comma should NOT be in italics.")

        cursor += 2

        # check for volume number
        self.citation_status = APACitationStatus.VOLUME

        volume = ""
        while citation[cursor] != "(":
            volume += citation[cursor]
            cursor += 1
            
        if "<i>" not in volume or "</i>" not in volume:
            raise Exception("The volume number should be italicized, and the comma that precedes the volume number should not be italicized.")

        volume = volume.replace("<i>", "")
        volume = volume.replace("</i>", "")

        if not volume.isdigit():
            raise Exception("Bad formatting in the volume number: '" + volume + "'")

        self.volume = volume

        cursor += 1

        # check for issue number
        self.citation_status = APACitationStatus.ISSUE

        issue = ""
        while citation[cursor] != ")":
            issue += citation[cursor]
            cursor += 1

        if not issue.isdigit():
            raise Exception("Bad formatting in the issue number: '" + issue + "'")

        self.issue = issue

        if citation[cursor + 1: cursor + 3] != ", ":
            if citation[cursor + 1] == ".":
                self.warnings.append("no page numbers found")
            else:
                raise Exception("Bad formatting in the issue number: '" + issue + "'")

        else:
            cursor += 3

            # check for page number
            self.citation_status = APACitationStatus.PAGES

            pages = ""
            pageNumbers = []

            while citation[cursor] != ".":
                pages += citation[cursor]
                cursor += 1

            if not re.match("^[0-9]+[-][0-9]+$", pages) and not re.match("^[0-9]+$", pages) and not re.match("^[0-9]+[–][0-9]+$", pages):
                if "http://" in pages or "https://" in pages:
                    raise Exception("The URL must be preceded by a period, not a comma.")
                else:
                    raise Exception("Bad formatting in the page number section: '" + pages + "'")

            if "-" in pages:
                pageNumbers = pages.split("-")
            elif '–' in pages:
                pageNumbers = pages.split("–")
            else:
                pageNumbers = [pages]

            self.pages = pageNumbers

        # check url
        self.citation_status = APACitationStatus.URL

        if "http://" in citation or "https://" in citation:
            cursor = citation.index("http://" if "http://" in citation else "https://")
            url = citation[cursor:]
            # conn = HTTPConnection(url)
            # conn.request("HEAD", '')
            # if conn.getresponse().status >= 400:
            #     raise Exception("Invalid URL: '" + url + "'")

            self.url = url

class MLACitationStatus(str, Enum):
    YEAR = "year"
    AUTHOR = "author"
    TITLE = "title"
    JOURNAL = "journal"
    URL = "url"
    OTHER_INFO = "other info"


class MLACitation():
    def __init__(self):
        self.authors = []
        self.title = ""
        self.year = ""
        self.url = ""
        self.otherInfo = []
        self.citation_status = MLACitationStatus.YEAR
        self.warnings = []

    def __str__(self):
        return "Author(s): " + str(self.authors) + "\n" + \
            "Year: " + self.year + "\n" + \
            "Title: " + self.title + "\n" + \
            "Other Info: " + str(self.otherInfo) + "\n" + \
            "URL/DOI: " + self.url + "\n" + \
            "Warnings: " + str(self.warnings) + "\n"

    def get_warnings(self):
        return "; ".join(self.warnings)

    def filter_latin(self, text):
        # get rid of any non-English alphabetic characters (vowels w/ accents, etc.)
        filtered_authors = ""

        for i in text:
            if(192 <= ord(i) <= 222):
                filtered_authors += 'X'
            elif(223 <= ord(i) <= 255):
                filtered_authors += 'x'
            else:
                filtered_authors += i

        return filtered_authors

    def check_citation(self, citation): 
        #NOTE: when implementing, wrap the method in a try catch and print out any error + the citation status

        try:
            pattern = re.compile("[ ][0-9]{4}")
            result = pattern.search(citation)
            self.year = result.group(0)[1:]
        except:
            raise Exception("Unable to find year in citation.")

        self.citation_status = MLACitationStatus.AUTHOR
            
        cursor = 0

        while True:
            ascii_value = ord(citation[cursor])

            # check if the current character is not " &-'." or any alphanumeric in English or Latin-1
            if citation[cursor : cursor + 2] != ". " and (ascii_value == 32 or ascii_value == 39 or 44 <= ascii_value <= 46 or 65 <= ascii_value <= 90 or 97 <= ascii_value <= 122 or 192 <= ascii_value <= 255):
                cursor += 1
            else:
                break

        if cursor != 0:
            author_section = ""
            if citation[cursor : cursor + 2] == ". ":
                author_section = citation[:cursor + 1]
            else:
                raise Exception("Bad formatting in the author section (unknown error).")
            
            # three or more authors
            if ", et al." in author_section:
                temp = author_section.replace(", et al", "")
                authors = temp.split(", ")
                filteredAuthor = [self.filter_latin(i) for i in authors]

                if re.match("^[A-Za-z][A-Za-z-' ]+$", filteredAuthor[0]) is not None \
                and re.match("^[A-Z][A-Za-z-'. ]+[.]$", filteredAuthor[1]) is not None:
                    self.authors.append(authors[0] + ", et al.")
                else:
                    raise Exception("Bad formatting in the author section: '" + author_section + "'")

            # two authors
            elif ", and " in author_section:
                authors = author_section.split(", and ")
                if ", " not in authors[0]:
                    raise Exception("Bad formatting in the author section: '" + author_section + "'")

                firstAuthor = authors[0].split(", ")
                filteredFirstAuthor = [self.filter_latin(i) for i in firstAuthor]

                if re.match("^[A-Za-z][A-Za-z-' ]+$", filteredFirstAuthor[0]) is not None \
                and re.match("^[A-Z][A-Za-z-'. ]+$", filteredFirstAuthor[1]) is not None:
                    self.authors.append(firstAuthor[0])
                else:
                    raise Exception("Bad formatting in the author section: '" + author_section + "'")

                if " " not in authors[1]:
                    raise Exception("Bad formatting in the author section: '" + author_section + "'")

                secondAuthor = authors[1].split(" ", 1)
                filteredSecondAuthor = [self.filter_latin(i) for i in secondAuthor]

                if re.match("^[A-Z][A-Za-z-']+$", filteredSecondAuthor[0]) is not None \
                and re.match("^[A-Za-z][A-Za-z-'. ]+[.]$", filteredSecondAuthor[1]) is not None:
                    self.authors.append(filteredSecondAuthor[1][:-1])

                elif re.match("^[A-Za-z][.]$", filteredSecondAuthor[1]) is not None:
                    author_cursor = cursor + 2
                    actualSecondAuthor = ""

                    while citation[author_cursor : author_cursor + 2] != ". ":
                        actualSecondAuthor += citation[author_cursor]
                        author_cursor += 1
                    
                    self.authors.append(actualSecondAuthor)

                else:
                    raise Exception("Bad formatting in the author section: '" + author_section + "'")
            
            # one author
            elif ", " in author_section:
                authors = author_section.split(", ")
                filteredAuthor = [self.filter_latin(i) for i in authors]

                if re.match("^[A-Za-z][A-Za-z-' ]+$", filteredAuthor[0]) is not None \
                and re.match("^[A-Z][A-Za-z-' ]+[.]$", filteredAuthor[1]) is not None:
                    self.authors.append(authors[0])
                else:
                    raise Exception("Bad formatting in the author section: '" + author_section + "'")

            elif "et. al." in author_section or "et.al." in author_section:
                raise Exception("'Et al.' should not have a period after the 'Et'.")
            # no match; bad formatting 
            else:
                raise Exception("Bad formatting in the author section: '" + author_section + "'")

        self.citation_status = MLACitationStatus.TITLE
        cursor += 1
        # check the title section
        if citation[cursor : cursor + 3] == "<i>":
            cursor += 3
        elif citation[cursor + 1 : cursor + 4] == "<i>":
            cursor += 4
        elif citation[cursor + 1] == "\"":
            cursor += 2
        elif citation[cursor - 1 : cursor + 1] == ".\"":
            raise Exception("Bad formatting in the title section.")

        title = ""

        while citation[cursor] != ".":
            title += citation[cursor]
            cursor += 1

        title = title.replace("\"", "")
        title = title.replace("</i>", "")

        if title[0] == " ":
            title = title[1:]
        
        if citation[cursor + 1] == "\"":
            cursor += 2
        else:
            cursor += 1
        #now cursor should be at the beginning of italics

        result = url("https://brettterpstra.com/titlecase/?title=" + title)
        title_cased_title = result.read().decode('utf-8')

        if title != title_cased_title:
            self.warnings.append("the title might contain improper capitalization: '" + title + "'")

        self.title = title

        # check for url
        self.citation_status = MLACitationStatus.URL

        extractor = URLExtract()
        if extractor.has_urls(citation):
            urls = extractor.find_urls(citation)
            self.url = urls[0][:-1]
            if self.url + "." not in citation: 
                raise Exception("Bad formatting in the URL section.")
            # try:
            #     conn = HTTPConnection('http://' + self.url)
            #     conn.request("HEAD", '')
            #     if conn.getresponse().status >= 400:
            #         raise Exception("Invalid URL: '" + url + "'")
            # except:
            #     try:
            #         conn = HTTPSConnection('https://' + self.url)
            #         conn.request("HEAD", '')
            #         if conn.getresponse().status >= 400:
            #             raise Exception("Invalid URL: '" + url + "'")
            #     except:
            #         raise Exception("Invalid URL: '" + url + "'")
            
            if citation[cursor : cursor + 3] != "<i>" and citation[cursor + 1 : cursor + 4] != "<i>":
                self.warnings.append("the container may not exist or may not be italicized")

        elif citation[cursor : cursor + 3] == "<i>" and citation[cursor + 1 : cursor + 4] == "<i>":
            self.warnings.append("the container might exist when not necessary (if the citation is about a book), or the block immediately following the title may be improperly italicized.")

        if self.url != "":
            citation.replace(self.url + ".", "")

        # check for other info
        # right now, it's too complex to validate the entire MLA citation without prior knowledge on what type of citation it is, 
        # so the other info is just stored without checking
        self.citation_status = MLACitationStatus.OTHER_INFO

        remainingText = citation[cursor:]
        info = remainingText.split(", ")
        self.otherInfo = [i for i in info]
