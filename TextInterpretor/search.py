import string
import datetime
import re
from babel.dates import format_date, format_datetime, format_time
import pyodbc

import speech_recognition as sr
from pydub import AudioSegment
import wave
import contextlib

# ----
def fctn():
    r = sr.Recognizer()
    src = "jumatate.mp3"
    dst = "test.wav"

    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")

    with contextlib.closing(wave.open('test.wav', 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    result = ""
    barbu = sr.AudioFile('test.wav')
    with barbu as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        while duration > 0:
            audio = r.record(source, duration=12)

            try:
                text = r.recognize_google(audio, language='ro-RO')
                result = text
            except:
                result = "Imi pare rau! Nu s-a inteles ce ai vrut sa spui...'"
            finally:
                duration -= 12
    return result
# ---

def search_for_question_keyword(filename, listwords):
    try:
        file = open(filename, "r")
        read = file.readlines()
        file.close()
        for word in listwords:
            lower = word.lower()
            for sentance in read:
                line = sentance.split()
                for each in line:
                    line2 = each.lower()
                    line2 = line2.strip("!@#$%^&*()_-.?;,/")
                    if lower == line2:
                        return lower

    except FileExistsError:
        return "The file is not here"


def prepare(input):
    split = [word.strip(string.punctuation) for word in input.split()]
    keyword = search_for_question_keyword("location.txt", split)
    # returnam propozitia splituita in cuvinte si keyword-ul definitoriu al intrebarii (Unde/cand)
    return (split, keyword)


def searchForDate(splitInput):
    ret = ""
    if splitInput == "The file is not here":
        ret = "ERROR"
        return ret

    dateWords = ["ieri", "alaltaieri", "azi", "astazi"]
    daysOfTheWeek = ["luni", "marti", "miercuri", "joi", "vineri", "sambata", "duminica"]
    now = datetime.date.today()
    for word in splitInput:
        if word in dateWords:
            if word == "astazi" or word == "azi":
                return now
            if word == "ieri":
                return now - datetime.timedelta(days=1)
            if word == "alaltaieri":
                return now - datetime.timedelta(days=2)

        elif word in daysOfTheWeek:
            for dayMinus in range(0, 7):
                date = now - datetime.timedelta(days=dayMinus)
                day_of_week = date.weekday()
                day = daysOfTheWeek[day_of_week]
                if word == day:
                    return date

        elif re.findall("[0-3][0-9]/[0-1][0-9]/[0-2][0-9][0-9][0-9]", word):  #cautam data de forma 31/12/2020
            return datetime.datetime.strptime(re.findall("[0-3][0-9]/[0-1][0-9]/[0-2][0-9][0-9][0-9]", word)[0], "%d/%m/%Y")  #transformam data(care e acum string) in tipul datetime

        elif re.findall("[0-3][0-9]/[0-1][0-9]", word):  #cautam data de forma 31/12 (fara an) -> ne va returna data din anul curent
            return datetime.datetime.strptime(re.findall("[0-3][0-9]/[0-1][0-9]", word)[0] + '/' + str(datetime.date.today().year), "%d/%m/%Y")  #adaugam current year la data noastra
    return ret


def searchForHour(splitInput):
    ret = ""
    for word in splitInput:
        found = re.findall("[0-2][0-9]:[0-6][0-9]", word)
        if found:
            return found[0]
    return ret


def reach_wrong_word(word):
    stop_at_word = ["saptamana", "ieri", "alaltaieri", "azi", "astazi", "luni", "marti", "miercuri", "joi", "vineri",
                    "sambata", "duminica", "luna", "anul", "ziua"]
    if word.lower() in stop_at_word:
        return True
    return False


def search_for_location(splitInput):
    ret = ""
    for i in range(0, len(splitInput)):
        if splitInput[i].upper() in ["LA", "PE"]:  #"La facultate" / "La adresa str. M.Viteazu" / "Pe strada aurel vlaicu" / "Pe Bahlui"
            if splitInput[i].upper() == "LA" and splitInput[i + 1].upper() == "ADRESA":
                i += 1  # skip peste cuvantul adresa
            i += 1
            while i < len(splitInput) and reach_wrong_word(splitInput[i]) == False:
                ret += splitInput[i]
                ret += ' '
                i += 1
            break
    if ret[ret.__len__()-1] == ' ':
        ret = ret[:-1]
    return ret


def call_database_for_answer(type_of_answer, datas):
    # create conn //sql server
    # tablename = "gps_data"
    # database  = "tiln"
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                          'Server=(LocalDB)\localdb;'
                          'Database=tiln;'
                          'Trusted_Connection=yes;')

    cursor = conn.cursor()
    sql_select = ""  #construim selectul

    if type_of_answer == "datetime":  #daca dorim un raspuns ce ne indica timpul (ex: I:"cand am fost la facultate", R:<data><ora>)
        sql_select = "SELECT [ORA], [DATA], [ADRESA] FROM [TILN].[DBO].[GPS_DATA] where LOWER(adresa) like '%" + datas.lower() + "%'"  #avem grija sa convertim atat stringul gasit in intrebare cat si cel gasit in db la litere mici

    if type_of_answer == "location": #daca dorim un raspuns ce ne indica locatia (ex: I:"unde am fost ieri", R:<locatie>)
        if datas[1] == "00:00:00":
            sql_select = "SELECT [ORA], [DATA], [ADRESA] FROM [GPS_DATA] where data = '" + datas[0] + "'"
        else:
            sql_select = "SELECT [ORA], [DATA], [ADRESA] FROM [GPS_DATA] where data = '" + datas[0] + "'and ora like '" + datas[1] + "%'"

    cursor.execute(sql_select)  #executare select
    row = cursor.fetchone()  #extrage primul rand din rezutat

    #construire raspuns
    if type_of_answer == "datetime" and row:
        return "Ai fost la "+row[2].strip()+" in data "+row[1].strip()+" ora " + row[0].strip()
    if type_of_answer == "location" and row:
        return "Ai fost la " + row[2].strip() + " in data " + row[1].strip() + " ora " + row[0].strip()
    return "Nu este inregistrata aceasta deplasare."


def searchInDatabase(splitInput, keyword):
    if keyword == "The file is not here":
        answer = "ERROR"
        return answer
    answer = "Fara raspuns valid"

    if keyword == 'unde':
        date = searchForDate(splitInput)
        time = searchForHour(splitInput)
        if date == "":
            datetime.date.now()
        if time == "":
            time = "00:00:00"
        # finaldate = str(date.day) + '/' + str(date.month) + '/' + str(date.year)  #pentru teste
        answer = call_database_for_answer("location", (date.strftime("%d/%m/%Y"), time))

    if keyword == 'cand':
        location = search_for_location(splitInput)
        answer = call_database_for_answer("datetime", location)
    return answer

# test
props = [
    "Unde ai fost vineri la ora 14:30 ?",
    "Cand am fost la facultate?",
    "Cand ai fost pe strada albinutelor?",
    "Unde ai fost ieri?",
    "Cand ai fost la Casa de cultura?",
    "Unde ai fost in data de 02/05/2020?",
    "Unde ai mers pe 10/10?"
]

# for prop in props:
#     print("Intrebare pusa: ", prop)
#     rez = prepare(prop)
#     print(searchInDatabase(rez[0], rez[1]))
#     print()

prop = fctn()
print("Intrebare pusa: ", prop)
rez = prepare(prop)
print(searchInDatabase(rez[0], rez[1]))
print()