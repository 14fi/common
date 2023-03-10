from common.constants import bcolors
from common import generalUtils
from objects import glob
import time
import os
from secret.discord_hooks import Webhook

ENDL = "\n" if os.name == "posix" else "\r\n"

def logMessage(message, alertType = "INFO", messageColor = bcolors.ENDC, discord = None, alertDev = False, of = None, stdout = True):
	"""
	Log a message

	:param message: message to log
	:param alertType: alert type string. Can be INFO, WARNING, ERROR or DEBUG. Default: INFO
	:param messageColor: message console ANSI color. Default: no color
	:param discord: Discord channel acronym for Schiavo. If None, don't log to Discord. Default: None
	:param alertDev: 	if True, developers will be highlighted on Discord.
						Obviously works only if the message will be logged to Discord.
						Default: False
	:param of:	Output file name (inside .data folder). If None, don't log to file. Default: None
	:param stdout: If True, log to stdout (print). Default: True
	:return:
	"""
	discordmsg = False
	# Get type color from alertType
	if alertType == "INFO":
		typeColor = bcolors.GREEN
	elif alertType == "WARNING":
		discordmsg = True
		typeColor = bcolors.YELLOW
	elif alertType == "ERROR":
		discordmsg = True
		typeColor = bcolors.RED
	elif alertType == "CHAT":
		typeColor = bcolors.BLUE
	elif alertType == "DEBUG":
		typeColor = bcolors.PINK
	else:
		typeColor = bcolors.ENDC

	# Message without colors
	if alertType == "DEBUG":
		ctime = float(time.time())
		finalMessage = "[{time}|since last msg: {lastmsg}] {type} - {message}".format(time=generalUtils.getTimestamp(), lastmsg=ctime - glob.time_since_last_debug_log, type=alertType, message=message)
		# Message with colors
		finalMessageConsole = "{typeColor}[{time}|since last msg: {lastmsg}] {type}{endc} - {messageColor}{message}{endc}".format(
			time=generalUtils.getTimestamp(),
			lastmsg = ctime - glob.time_since_last_debug_log,
			type=alertType,
			message=message,
			typeColor=typeColor,
			messageColor=messageColor,
			endc=bcolors.ENDC)
		glob.time_since_last_debug_log = float(time.time())
	else:
		finalMessageConsole = "{typeColor}[{time}] {type}{endc} - {messageColor}{message}{endc}".format(
		time=generalUtils.getTimestamp(),
		type=alertType,
		message=message,

		typeColor=typeColor,
		messageColor=messageColor,
		endc=bcolors.ENDC)
		finalMessage = "[{time}] {type} - {message}".format(time=generalUtils.getTimestamp(), type=alertType, message=message)


	# Log to console
	if stdout:
		print(finalMessageConsole)



	# Log to discord if needed
	if discord is not None:
		if discord == "ac":
			webhook = Webhook(glob.conf.config["discord"]["ahook"],
				color=0xc32c74,
				footer="gaming")
			webhook.set_footer(text="Anticheat")
	else:
		webhook = Webhook(glob.conf.config["discord"]["devgroup"],
				color=0xc32c74,
				footer="gaming")
		webhook.set_footer(text="Error")

	# Log to file if needed
	if of is not None:
		glob.fileBuffers.write(".data/"+of, finalMessage+ENDL)
	if discordmsg == True:
		if glob.conf.config["discord"]["enable"]:
			webhook.set_title(title=f"log")
			webhook.set_desc(f'{message}')
			webhook.set_footer(text="alertType")
			webhook.post()


def warning(message, discord = None, alertDev = False):
	"""
	Log a warning to stdout and optionally to Discord

	:param message: warning message
	:param discord: Discord channel acronym for Schiavo. If None, don't log to Discord. Default: None
	:param alertDev: 	if True, developers will be highlighted on Discord.
						Obviously works only if the message will be logged to Discord.
						Default: False
	:return:
	"""
	logMessage(message, "WARNING", bcolors.YELLOW, discord, alertDev)

def error(message, discord = None, alertDev = True):
	"""
	Log a warning message to stdout and optionally to Discord

	:param message: warning message
	:param discord: Discord channel acronym for Schiavo. If None, don't log to Discord. Default: None
	:param alertDev: 	if True, developers will be highlighted on Discord.
						Obviously works only if the message will be logged to Discord.
						Default: False
	:return:
	"""
	logMessage(message, "ERROR", bcolors.RED, discord, alertDev, of = "errors.txt")

def info(message, discord = None, alertDev = False):
	"""
	Log an info message to stdout and optionally to Discord

	:param message: info message
	:param discord: Discord channel acronym for Schiavo. If None, don't log to Discord. Default: None
	:param alertDev: 	if True, developers will be highlighted on Discord.
						Obviously works only if the message will be logged to Discord.
						Default: False
	:return:
	"""
	logMessage(message, "INFO", bcolors.ENDC, discord, alertDev)

def debug(message):
	"""
	Log a debug message to stdout.
	Works only if the server is running in debug mode.

	:param message: debug message
	:return:
	"""
	if glob.debug:
		logMessage(message, "DEBUG", bcolors.PINK, of = "debug.txt")

def chat(message):
	"""
	Log a public chat message to stdout and to chatlog_public.txt.

	:param message: message content
	:return:
	"""
	logMessage(message, "CHAT", bcolors.BLUE, of="chatlog_public.txt")

def pm(message):
	"""
	Log a private chat message to stdout. Currently not used.

	:param message: message content
	:return:
	"""
	logMessage(message, "CHAT", bcolors.BLUE)

def rap(userID, message, discord=False, through=None):
	"""
	Log a message to Admin Logs.

	:param userID: admin user ID
	:param message: message content, without username
	:param discord: if True, send the message to discord
	:param through: through string. Default: FokaBot
	:return:
	"""
	if through is None: #Set default messager to bot account
		through = glob.BOT_NAME

	import common.ripple
	glob.db.execute("INSERT INTO rap_logs (id, userid, text, datetime, through) VALUES (NULL, %s, %s, %s, %s)", [userID, message, int(time.time()), through])
	username = common.ripple.userUtils.getUsername(userID)
	logMessage("{} {}".format(username, message), discord=discord)
