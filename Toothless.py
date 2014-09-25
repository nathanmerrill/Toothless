from selenium import webdriver
from time import sleep
import fourFn
import sys
from selenium.common.exceptions import *
from User import *
from Query import *
import difflib


def close_browser():
    for user_list in users:
        for user in user_list:
            user.update_favor()
    write_users()
    browser.execute_script("window.open('','_self').close()")
    browser.quit()
    return 0


def make_admin(*args):
    name = args[0]
    for user_list in users:
        for user in user_list:
            if user.name.lower() == name.lower():
                user.is_admin = True
                user.update = True
                return "Done"
    return "No such user"


def login():
    global browser
    browser = webdriver.Chrome()
    browser.get(gs_url)
    browser.implicitly_wait(10)
    browser.find_element_by_id("header-login-btn").click()
    browser.find_element_by_id("login-username").send_keys(username)
    browser.find_element_by_id("login-password").send_keys(password)
    browser.find_element_by_css_selector(".submit").click()
    sleep(1)
    browser.get(mos_url)
    browser.find_element_by_id("bc-action-btn").click()
    sleep(1)
    browser.execute_script("GS.Services.SWF.sendBroadcastChat('*meep*')")
    browser.execute_script("$('.chat-message').addClass('read')")
    sleep(1)
    browser.find_element_by_id("volume").click()


def send_chat(mes):
    if not mes:
        return
    global last_chat
    try:
        if mes == last_chat:
            m = "* "+mes+" *"
        else:
            m = "*"+mes+"*"
        last_chat = mes
        m = ''.join([i if ord(i) < 128 else ' ' for i in m])
        m = m.replace('\n', "")
        print "\t"+m
        browser.execute_script("GS.Services.SWF.sendBroadcastChat(\""+m+"\")")
    except WebDriverException:
        pass


def update_phrases(phrase=None):
    if phrase:
        phrase_file = open("phrases.txt", "a")
        phrase_file.write("\n"+phrase.lower())
        phrase_file.close()
    phrase_file = open("phrases.txt")
    full_phrases = phrase_file.read().splitlines()
    phrase_file.close()
    for full_phrase in full_phrases:
        query = Query()
        if full_phrase.startswith("!"):
            query.is_important = True
            full_phrase = full_phrase[1:]
        inp, out = full_phrase.split("/")
        query.add_inputs(inp.split(","))
        query.add_string_outputs(out.split(","))
        queries.append(query)
    return "jumps to it"


def learn(message, user):
    if message.count('/') != 1:
        return ""
    return update_phrases(message)


def should_respond_to(user, message):
    if user.id == toothlessId:
        return False
    if "http" in message:
        return False
    for x in names:
        if x in message:
            return True
    return False


def parse_message(message, user):
    lower = message.lower()
    if not should_respond_to(user, lower):
        try:
			if "toothless" not in lower:
				if difflib.get_close_matches("toothless", str(lower).split(" "), 1, .8):
					send_chat("ignores "+user.name)
					user.favor -= 2
        except UnicodeEncodeError:
            pass
        return
    print message
    if user.is_spamming():
        send_chat("*isn't listening*")
        user.num_spams += 1
        user.favor -= user.num_spams
        return
    max_priority = 0
    next_response = Response()
    for query in queries:
        priority, response = query.matches(message, user)
        if priority > max_priority:
            next_response = response
            max_priority = priority
    send_chat(next_response.respond(user))


def parse_messages():
    messages = browser.execute_script(script)
    for message in messages:
        new_user, content = create_from_element(message)
        user = get_user(new_user)
        user.name = new_user.name
        user.is_admin = new_user.is_admin or user.is_admin
        parse_message(content, user)


def score(name, amount):
    name = str(name.lower()).strip()
    if name in scores.keys():
        scores[name] = amount + scores[name]
    else:
        scores[name] = amount
    return str(scores[name])


def max_score():
    maxscore = 0
    top_users = set()
    for user, score in scores.iteritems():
        if score > maxscore:
            top_users.clear()
            maxscore = score
            top_users.add(user)
        elif score == maxscore:
            top_users.add(user)
    if top_users:
        return ", ".join(top_users)+" with a score of " + str(maxscore)
    return "thinks that nobody has scored"


def score_of(name):
    name = str(name.lower())
    if name not in scores:
        return "0"
    return str(scores[name])

def upvote_song():
    if "btn-success" not in browser.find_element_by_css_selector(".btn.upvote").get_attribute("class"):
        browser.find_element_by_css_selector(".btn.upvote").click()
        return "dances around"
    return ""

browser = None
gs_url = "http://grooveshark.com/"
mos_url = gs_url+"#!/masterofsoundtrack/broadcast"
username = "masteroftoothless"
password = "calculate"
nsp = fourFn.NumericStringParser()
toothlessId = 21218701
teeId = 1217114
queries = []
scores = {}
last_chat = ""
script = "a=[];$('.chat-message:not(\".read\")').each(function(index, element){user = element.getElementsByClassName('user-name')[0];message = element.getElementsByClassName('message')[0].innerText;id=user.attributes['data-user-id'].value;name=user.text;admin=element.classList.contains('chat-vip')||element.classList.contains('chat-owner')||id==\"121711\";a.push(id+'\\t'+name+'\\t'+admin+'\\t'+message);element.classList.add('read');});return a"



admin_commands = [
    ("learn", learn),
    ("toothless leave", lambda *args: sys.exit(close_browser())),
    ("make admin", lambda s, user: find_user_by_name(s).make_admin()),
    ("unscore user", lambda s, user: score(s, -1)),
    ("score user", lambda s, user: score(s, 1)),
    ("refresh", lambda s, user: update_phrases()),
]

special_responses = [
    ("tell me something", lambda *args: random.choice(trivia)),
    ("calculate", lambda s, user:nsp.eval(s)),
    ("top score", lambda s, user: max_score()),
    ("score of", lambda s, user: score_of(s.lower())),
    ("my score", lambda s, user: score_of(user.name.lower())),
    ("upvote this song", lambda s, user: upvote_song() if user.calculate_favor() > 90 else "only upvotes good songs"),
    ("how many commands do you know", lambda *args: str(len(queries))),
    ("your mood", lambda *args: [
        "is depressed",
        "is sad",
        "is ok",
        "is decent",
        "is happy"
    ].__getitem__(min((int((mood+20)/8), 4)))),
]

for word, command in admin_commands:
    queries.append(Query().add_input(word).add_output(command).is_admin())

for word, command in special_responses:
    queries.append(Query().add_input(word).add_output(command).make_important())


names = [
    "toothless",
    "night fury",
    "httyd",
    "fish",
	"gbbguyrff",
]

while True:
    try:
        read_users()
        trivia_file = open("trivia.txt")
        trivia = trivia_file.read().splitlines()
        trivia_file.close()
        update_phrases()
        login()
        while True:
            parse_messages()
            try:
                if "icon-heart-color-flat" in browser.find_element_by_css_selector(".icon.heart").get_attribute("class"):
                    send_chat(upvote_song())
            except WebDriverException:
                pass
            browser.execute_script("Grooveshark.addCurrentSongToLibrary()")

    except Exception:
        close_browser()
        raise
