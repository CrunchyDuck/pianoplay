import bpy
import math
from pathlib import Path

# noinspection PyRedundantParentheses
class PianoPlay():
	def __init__(self):
		### USER VARIABLES ###
		# You, the user, have to fill in the following variables.

		self.objectName = "CDPKey"  # This is the name it will search for on the objects that you would like to apply the animations to. It'll find all objects with this name, and then order by the suffix number.
			# E.G CDPKey.000, CDPKey1, CDPKey2.
			# The lower numbered objects will have the lower pitch notes, E.G CDPKey0 will have pitch 0, CDPKey1 will have pitch 1, CDPKey2 will have pitch 2...
		self.keyNum = 128 # How many keys we'll want to index. There is a maximum of 128 on MIDI files.
		self.pitchStart = 0  # The pitch that the lowest key will have. 0 is the lowest pitch.
			# This is based on the MIDI indexing, so pitchStart 60 is C4. pitchStart 0 is C0.
			# It will count up keyNum times from this position.
			# Pitches in the MIDI file that aren't within this range will be ignored.
		fileName = "myuu - Reversion.mid"  # The location of the file on the hard drive.
			# It must include the file extension E.G .mid, .midi, .txt, and must be the full path, E.G C:/Users/Me/Music/song.mid
		self.FPS = 60 # This is an integer. It will be the frame rate that the final animation of the instrument should be played at.
			# This should be the same as the frame rate of blender if you don't know what you're doing.
			# A higher frame rate will mean more accurate timing and more fluid looking animations.
		self.frameStart = 100 # The frame that the animation should start on.





























		### Built in variables ###
		# Don't change these if you don't know what you're doing.
		# Also, if you're reading this, you're likely going through my code with intent to change it.
		# I'd like to apologize in advance - This is my first time using Python seriously, I hail from C# and GML myself.
		# I also don't like Python much, so I've admittedly been mean to it and didn't put the time in to learn stuff like scope properly.
		# I hope it's not too difficult for you to work with. I'll give a couple of resources about MIDI works, to help you understand it:
		# https://www.music-software-development.com/midi-tutorial.html
		# https://www.midi.org/specifications-old/item/the-midi-1-0-specification
		# You'll need to make an account for that last one, but it's also the most important. It explains how the data in MIDI is stored, especially under the segment about "Chunking"

		self.fileLocation = Path(__file__).parent.parent + "\\MIDI\\" + fileName
		self.output = FileManager()
		self.projName = "PianoPlay"
		self.ex = "Exiting " + self.projName + " script..." # Just the exiting message.
		self.debug = True # This will enable more messages in the console window. I put these behind a "debug" check because it gets spammy quick.
		self.headerFormat = 0  # The format for the MIDI heading. 0, 1 or 2. Explained in the MIDI specifications.
		self.trackNum = 0  # Used for MIDI encoding, the amount of tracks present in the file.
		self.errTriggered = False  # If this is true, then the programme has run into an error and will immediately break out of running the rest. I'll put a check for this at the start of all functions that can be skipped by an error occurring.
		self.deltaFormat = 0  # The format of delta-timing the MIDI file uses. 0 or 1.
		self.ticksPerQuarterNote = 0  # This will heavily depend on the previous deltaFormat. God I hope I do this right.
		self.trackLength = 0 # The track length, in bytes.
		self.iTrackNum = 0 # Track num iterator. Temporary.
		self.realDeltaTime = 0 # The "real" delta time. Cumulative of the entire MTrk.
			# Values are in "ticks". I'll convert this to milliseconds ultimately.
			# In normal midi files, delta time listed is relative to the previous event. This is done to save space.
			# Storing it in real time rather than relative time will make it a fair bit easier for me to work with.
			# And really, do we care about individual bytes for my dumb niche programme? I'm honoured if you do. <3
		self.tempo = 500000 # The tempo is defined in "tempo set" events. It is assumed to be 500000 if not set.
			# Tempo is expressed as microseconds per quarter note. (eg. 500000 = 120 bpm).
		self.sustainInitialized = False # Whether there has been any elements added to the tempo array. If not, we'll overwrite the first, default values.

		# Lists
		self.objectList = [None for i in range(self.keyNum)] # This will list stored a reference to all of the objects we're going to apply animations to.
		self.tempoList = [0, 500000] # This is a 2D array. This will be resized with the .append() function.
		self.tempoBlock = [0] # These are the "blocks" of tempo. I'll use this to calculate the real millisecond time of delta events.
		self.sustainList = [0, False] # Column 1 is the delta time, column 2 is a true/false if the sustain pedal is pressed right now.
		self.keyPresses = [[0, False, 0] for i in range(self.keyNum)] # A 2D array that will store all of the key data.
			# The row represents the pitch of the key, calculated as (index) + self.pitchStart
			# Column 1 is the delta time. Column 2 is if it was pressed (true) or released (false). Column 3 is the velocity.

		# Animation variables:
		self.millisecondsPerFrame = (1 / self.FPS) * 1000
		self.velocityOffset = self.FPS * 0.3  # How many frames the velocity can offset a key. Should be relative to the FPS.
		self.pressTime = self.FPS * 0.05 # How long it should take for a key to be pressed at maximum velocity.
		self.releaseTime = self.FPS * 0.15 # How long it takes for a key to return to its original position when released.
		self.keyAngle = 3 # How much the key should rotate when pressed down, in Euler degrees.

		self.keyAngle = math.radians(self.keyAngle)

		print("---------------------------------------------")  # This just clears some space in the console. Makes it easier for me to read during testing.
		print("Running PianoPlay...")
		fileName = self.fileLocation.split("/") # This might cause errors on platforms that use \? I'll need to test.
		print("File name: " + fileName[-1])

		self.indexObjects()
		self.openFile()
		self.readFileSignature()

		# File formats
		if(self.output.asAscii() == "MThd"):
			self.readMidi()
		else:
			print("Unknown file signature, is it listed as recognized in the Python script?")

		self.animateKeys()


		if(self.errTriggered): # If we triggered an error, give an exit message.
			print(self.ex)


	def indexObjects(self):
		"""
		Checks if the animation can be found in Blender.
		If the value is set to "Null", it'll bypass this check.
		:return:
		"""
		if(self.errTriggered):
			return()


		# Find the objects by their names.
		for i in range(self.keyNum):
			number = "00" + str(i)
			number = number[-3:] # This will select the last 3 numbers from the string.
			name = self.objectName + "." + number
			self.objectList[i] = bpy.data.objects[name]

	def openFile(self):
		"""
		Open the specified file for reading.
		"""
		if(self.errTriggered):
			return()


		try:
			self.output.file = open(self.fileLocation, "rb")
		except Exception as e:
			print(e)
			self.errTriggered = True
			return()

	def readFileSignature(self):
		"""
		Read the first 4 bytes of the file. This will tell us what kind of file it is (E.G .mid)
		"""
		if (self.errTriggered):
			return()
		try:
			self.output.read(4) # First four bytes of the file should always be the ASCII file signature.
		except Exception as e:
			print(e)
			self.errTriggered = True
			return()

	def readHeaderSize(self):
		"""
		This part reads the header, bytes 5-8 of a file. This will give me length of the header. This is just to make
		sure the file is formed properly.
		"""
		if (self.errTriggered):
			return()


		self.output.read(4)

		if (self.output.asInt() == 6):
			print("Correct header length...")
		else:
			print("File header length isn't six bytes, cannot be read.")
			self.errTriggered = True
			return()

	def readHeaderFormat(self):
		"""
		Reads bytes 9 and 10 to find out the format of the tracks in the file.
		"""
		if (self.errTriggered):
			return()


		self.output.read(2)
		self.headerFormat = self.output.asInt()

		# Imagine this next segment is a switch/case statement. Python doesn't have them built in. :/
		if (self.headerFormat == 0):
			print("MIDI header format 0 detected...")

		elif (self.headerFormat == 1):
			print("MIDI header format 1 detected...")

		elif (self.headerFormat == 2):
			# Like format 0 I don't know how to work 3, yet.
			print("MIDI header format 2 detected...")

		else:
			print("MIDI header format not recognized. Must be 0, 1 or 2.")
			self.errTriggered = True
			return()

	def readTrackNum(self):
		"""
		Read bytes 9 and 10, tells us how many "MTrk" (tracks) headers are in the file.
		"""
		if (self.errTriggered):
			return()


		self.output.read(2)

		if (self.output.asInt() > 0):
			self.trackNum = self.output.asInt()
			print(str(self.output.asInt()) + " track(s) detected.")
		else:
			print("Number of tracks in the MIDI header isn't more than 0, and cannot be read.")
			self.errTriggered = True
			return()

	def readTrackDivision(self):
		"""
		Reads the final bytes of the header, bytes 11-14.
		This defines the speed of the music, and the type of delta-time used. See the MIDI specifications for more info.
		"""
		if (self.errTriggered):
			return()


		self.output.read(2)
		# Read the "flag" byte. This will tell me what delta-time format the MIDI file uses.
		self.deltaFormat = (self.output.asInt() & (1 << 15)) >> 15  # This has to be bit shifted to position 16, as we're dealing with a 16 bit number.

		if (self.deltaFormat == 0):
			self.ticksPerQuarterNote = self.output.asInt()  # If we're in deltaFormat 0, the number stored in output will already be correct.
			print("Delta-timing format 0 detected. Ticks per quarter-note is " + str(self.ticksPerQuarterNote))
		else:
			print("Delta-timing format 1 detected. I don't know how to do this at the time of writing this code."
				  "If you see this, please contact me and tell me I forgot to do this.")

	def readTracks(self):
		"""
		This is where most of the data will be taken from.
		"""
		if (self.errTriggered):
			return()


		while(self.iTrackNum < self.trackNum):
			self.iTrackNum += 1
			self.realDeltaTime = 0
			status = 0 # This is the last "midi message" byte we had. This is important to store, as messages of the same type might have their status byte omitted.
			# Search for the letter "M". This is done because some MIDI tracks are wank and don't end at the time they say they do, leaving unused data at the end.
			x = 0

			for x in range(50): # If we go above 50 bytes, it's likely that we can't find an M after the end-of-track event like we expect and we are lost.
				self.output.read(1)
				asciiText = self.output.asInt() # We're storing this as an int just to make it a little easier for me to compare.

				if(asciiText == 0x4d): # Hex for "M"
					self.output.read(3)

					asciiText = (asciiText << 8 * 3) + self.output.asInt()
					if(asciiText == 0x4d54726b): # Hex for "MTrk"
						break

			if(x >= 49): # Exceeded M search capacity, exit the programme because we're lost as heck lmao
				print("M search capacity reached.")
				print("Seek position: " + str(self.output.file.tell()))
				self.errTriggered = True
				break

			self.output.read(4) # Read how large this chunk is in bytes. This likely won't be used since tracks have an "End of track" event.
			self.trackLength = self.output.asInt()

			# i = 0 # This is just an insurance counter. If we go too high, break the loop to stop a permanent loop.
			while(1):
				# i += 1
				# Read and add up the delta time.
				deltaTime = self.decodeVariableLengthQuantity()
				self.realDeltaTime += deltaTime
				print(self.realDeltaTime)


				# Read the first byte. I can parse this to know what kind of MIDI event is here. F0 and F7 events are skipped.
				self.output.read(1)
				val = self.output.asInt()

				# Meta event, like a tempo change.
				if(val == 0xff):
					nr = False # Short for "Not recognized." If this is triggered then we need to know what bytes weren't recognized.
						# I'll set this to trigger at any "loose ends", aka a place where we can't resolve to a function.
					val = self.output.read(1, outputType = 1)

					# Set tempo command.
					if(val == 0x51):
						self.output.read(1)
						val = (val << 8) + self.output.asInt()

						if(val == 0x5103):
							self.output.read(3)
							newTempo = self.output.asInt()

							if(self.realDeltaTime == 0):
								self.tempoList[0] = 0
								self.tempoList[1] = newTempo
							else:
								# This will overwrite the default value in the array the first time, and append from then on.
								self.tempoList.append(self.realDeltaTime)
								self.tempoList.append(newTempo) # Add a list to the end of the list.
						else:
							self.output.read(3)
							nr = True
					# Text event.
					elif(val == 0x01):
						length = self.decodeVariableLengthQuantity()
						self.output.skip(length)
					# End of track event. Very important we catch this one.
					elif (val == 0x2f):
						self.output.read(1)
						val = (val << 8) + self.output.asInt()

						if (val == 0x2F00):
							print("End of track number " + str(self.iTrackNum))
							break  # Reached the end of the track. Move on to the next track.
						else:
							nr = True
					# Instrument Name. Don't have something to reference to see if it's important.
					elif(val == 0x04):
						length = self.decodeVariableLengthQuantity()
						self.output.skip(length)
					# MIDI Channel Prefix. Don't have a file with this in it. Seems important.
					elif(val == 0x20):
						self.output.read(1)
						val = (val << 8) + self.output.asInt()

						if(val == 0x2001):
							self.output.skip(1)
						else:
							nr = True
					# SMPTE Offset. Don't know. Don't have something to reference. Probably important.
					elif(val == 0x54):
						self.output.read(1)
						val = (val << 8) + self.output.asInt()

						if(val == 0x5405):
							self.output.skip(5)
						else:
							nr = True
					# Time sig change/declaration. Don't care, not displaying sheets.
					elif(val == 0x58):
						self.output.read(1)
						val = (val << 8) + self.output.asInt()

						if(val == 0x5804):
							self.output.skip(4)
						else:
							nr = True
					# Key sig. Not displaying sheets. Not useful.
					elif(val == 0x59):
						self.output.read(1)
						val = (val << 8) + self.output.asInt()

						if(val == 0x5902):
							self.output.skip(2)
					# Sequencer-Specific Meta-Event. Not in the mood to read it right now. Doesn't seem important.
					elif(val == 0x7f):
						length = self.decodeVariableLengthQuantity()
						self.output.skip(length)
					# "Sequence Number" event.
					elif(val == 0x00):
						self.output.read(1)
						val = (val << 8) + self.output.asInt()

						if(val == 0x0002):
							self.output.skip(2)
						else:
							nr = True
					# Copyright bullshit.
					elif(val == 0x02):
						length = self.decodeVariableLengthQuantity()
						self.output.skip(length)
					# Sequence/Track Name.
					elif (val == 0x03):
						# This might be important to separate. Not sure.
						length = self.decodeVariableLengthQuantity()
						self.output.skip(length)
					# Lyrics. Don't think animations sing. Least not in the scope of my project.
					elif(val == 0x05):
						length = self.decodeVariableLengthQuantity()
						self.output.skip(length)
					# "Marker." Text. Probably not useful.
					elif(val == 0x06):
						length = self.decodeVariableLengthQuantity()
						self.output.skip(length)
					# Cue point. No.
					elif(val == 0x07):
						length = self.decodeVariableLengthQuantity()
						self.output.skip(length)
					# We don't know D:
					else:
						# We don't know where we are, we just need to step byte by byte till we find something we recognize.
						# I don't know if there's a better way of doing this. All I can imagine and read seems to suggest not.
						# Midi's docs do directly state that there will invariably be events that cannot be understood, and to prepare for them. This is that.
						nr = True

					if(nr == True): # If we couldn't resolve to a point where we could understand the code given, trigger the minor error message.
						valhex = hex(val) # Stored like this so that I can crop off the 0x at the start.
						print("Byte at seek position " + str(self.output.file.tell()) + " not recognized.\nStored bytes: 0xff" + valhex[2:])

				# These are "sysex" (System Exclusive) messages. As far as I know, these are not necessary for me to read.
				elif(val == 0xf0) or (val == 0xf7):
					length = self.decodeVariableLengthQuantity() # Read the length of this event and skip it.
					self.output.skip(length)

				# Check to see if it is a "MIDI message", such as a key press or sustain pedal press.
				else:
					# Status byte check. Note that this can be occasionally omitted if it's a repeat of the previous status.
					statusCheck = val >> 7 # This will only return the first bit in the byte. If it is set to 1, it is a status byte. If not, it is a data byte.
					if(statusCheck):
						# Check the first nibble of the byte to see what message it is.
						status = val
						dataByte1 = self.output.read(1, outputType = 1)
						dataByte2 = self.output.read(1, outputType = 1)
					else:
						# "status" will already be set if we're here, so we only need to fill in the dataBytes.
						dataByte1 = val
						dataByte2 = self.output.read(1, outputType = 1)

					# Check what message we have.
					midiMessage = status >> 4  # Leave only the first 4 bytes of the status message. The other 4 represent the channel, and for now I'm going to ignore channels.

					# Note on
					if (midiMessage == 0b1001):
						pitch = dataByte1
						keyIndex = pitch - self.pitchStart # This will check if the key's pitch is within range of the user's settings.

						# I'm certain the following code has to be inefficient.
						if(keyIndex >= 0) and (keyIndex < self.keyNum): # If the pitch is within range of the user's defined values...
							velocity = dataByte2

							self.keyPresses[keyIndex].append(self.realDeltaTime)

							if (velocity != 0):
								self.keyPresses[keyIndex].append(True)
							else: # Why tf does midi allow for this dumb shi-
								self.keyPresses[keyIndex].append(False)

							self.keyPresses[keyIndex].append(velocity)

					# Note off
					elif (midiMessage == 0b1000):
						print("Note off")
						pitch = dataByte1 # Pitch of the note
						keyIndex = pitch - self.pitchStart

						# I'm certain the following code has to be inefficient.
						if (keyIndex >= 0) and (keyIndex < self.keyNum):  # If the pitch is within range of the user's defined values...
							velocity = dataByte2

							self.keyPresses[keyIndex].append(self.realDeltaTime)
							self.keyPresses[keyIndex].append(False)
							self.keyPresses[keyIndex].append(velocity)

					# MIDI controller message.
					elif (midiMessage == 0b1011):
						ctrlNum = dataByte1

						# Sustain pedal.
						if(ctrlNum == 64):
							pedalValue = dataByte2

							if(self.sustainInitialized):
								self.sustainList.append(self.realDeltaTime)

								if(pedalValue < 64):
									self.sustainList.append(False)
								else:
									self.sustainList.append(True)
							else:
								self.sustainInitialized = True
								self.sustainList[0] = self.realDeltaTime

								if(pedalValue < 64):
									self.sustainList[1] = False
								else:
									self.sustainList[1] = True
						# Turn off all controllers currently active. For me right now, this will just turn off the sustain pedal.
						elif(ctrlNum == 121):
							self.sustainList.append(self.realDeltaTime)
							self.sustainList.append(False)
						# All notes off.
						elif(ctrlNum == 123):
							pos = 0
							while(pos < self.keyNum):
								self.keyPresses[pos].append(self.realDeltaTime)
								self.keyPresses[pos].append(False)
								self.keyPresses[pos].append(127)
								pos += 1
						# Unknown
						else:
							if(self.debug):
								print("MIDI controller byte at seek position " + str(self.output.file.tell()) + " not recognized. Controller number: " + hex(ctrlNum))

					else: # Otherwise, it's a function we're not going to use and we can ignore it. I'll list the functions I know of regardless.
						# 0b1110 == Pitch Bend. Audio function, we're not doing audio yet.
						# 0b1100 == Instrument Change. Same as pitch bend, not used.
						pass

	def readMidi(self):
		"""
		MIDI reading protocol. This will run all of the stuff required to decode a MIDI file.
		"""
		if (self.errTriggered):
			return()


		print("Detected MIDI file format...")

		self.readHeaderSize()
		self.readHeaderFormat()
		self.readTrackNum()
		self.readTrackDivision()
		self.readTracks()
		self.createTempoBlocks()
		self.convertDToM()

	def decodeVariableLengthQuantity(self):
		"""
		This is data stored as "Variable-length quantity", read the MIDI documentation for more info.

		I'll try to give an example. We have the hex sequence ff ff 56, written as 11111111 11111111 01010110.
		Because the most significant bit in each byte must unset, this becomes 7f 7f 56, or 01111111 01111111 01010110.
		I then need to add these together as if they were 7 bit numbers rather than 8 bit. To do this I have to "layer" and then add them, as shown below.
		01111111               +
			   01111111        +
					  01010110

		:return: Returns the decoded value.
		"""
		if (self.errTriggered):
			return()

		variableLengthQuantity = 0  # This will be used to temporarily store our "Variable-length" value during decoding.

		for i in range(6): # The cap should be 4 bytes, but the documentation was vague on this.
			self.output.read(1) # This is an instance of a file manager class thing I made, it just makes it easier for me to convert between data types.
			bitSignificance = (i * 7) # Uh, I can't think of how to explain this right now. I'm sorry.
			num = self.output.asInt()

			bit7Check = num >> 7  # Check if the first bit is set.
			if not bit7Check:
				variableLengthQuantity = (variableLengthQuantity << bitSignificance) + num # If the first bit isn't set then the value is below 0x80, and does not need the first bit unset.
				break
			else:
				bit7Unset = num & 0x7f # Unset the most significant bit of this byte.
				variableLengthQuantity = (variableLengthQuantity << bitSignificance) + bit7Unset

		return variableLengthQuantity

	def deltaTimeToMS(self, val):
		""" This takes a given value expressed in "delta time" and converts it to milliseconds.
		 Here's the formula, for my own sanity. (qn is quarter note)
		 Time (in ms.) = (Number of Ticks) * (Tempo (μs/qn) / Div (ticks/qn)) / 1000"""
		if (self.errTriggered):
			return()


		try:
			return val * (self.tempo / self.ticksPerQuarterNote) / 1000
		except ZeroDivisionError:
			print("Division by zero while converting delta time to milliseconds. Was ticksPerQuarterNote assigned a value?")
			self.errTriggered = True
			return()

	def createTempoBlocks(self):
		"""
		When the tempo changes, it will cause 1 delta tick to be longer or shorter.
		In order to figure out the correct delta time for an event, we'll need to figure out how long each "period" of tempo is.
		This is a terrible explanation, apologies. I'm not even quite sure myself.
		:return:
		"""
		if(self.errTriggered):
			return()



		numOfTempoChanges = len(self.tempoList) / 2 # We divide this by two, as each tempo change has two variables, delta-time and tempo.
		if(numOfTempoChanges > 1): # If there's more than one tempo change, then we can create tempo blocks.

			i = 0
			while(i < numOfTempoChanges - 1): # As the numOfTempoChanges is index 1 and we must look 1 index ahead, we need to subtract 1.
				self.tempo = self.tempoList[(i * 2) + 1] # This sets it to the tempo that we're creating a tempo block for.
				currentTempoDelta = self.tempoList[i * 2]
				nextTempoDelta = self.tempoList[(i + 1) * 2]

				duration = nextTempoDelta - currentTempoDelta # How many delta-ticks the selected tempo lasts for.
				durationMS = self.deltaTimeToMS(duration) # Convert this duration to milliseconds.

				if(i != 0):
					cumulativeMS = self.tempoBlock[i - 1] + durationMS # We'll be storing the blocks as their value, plus the value of all blocks before them.
					self.tempoBlock.append(cumulativeMS)
				else: # If this is the first tempo block we're creating, overwrite the null tempo block entry.
					self.tempoBlock[0] = durationMS # As this is the first entry, there is no blocks before it, and therefore nothing to accumulate.

				i += 1

	def convertDToM(self):
		"""This event will convert the sustain pedal delta times, and the key press delta times into real milliseconds."""
		if(self.errTriggered):
			return()


		numOfTempoChanges = len(self.tempoList) / 2
		if(numOfTempoChanges > 1): # We'll need to take tempoBlocks into account if there's more than one tempo.

			# Sustain pedal
			tempoIndex = 0 # This is going to be used to iterate through the tempo blocks.
			reachedEndOfTempoChanges = False
			currentTempoBlockMS = 0 # The value we'll fetch from the tempo block. Should start as 0.
			currentTempoDelta = 0 # The delta-time of the current tempo change. Used to calculate the difference between the last tempo block, and the current event
			nextTempoDelta = self.tempoList[2] # The delta-time of the next tempo change. If our event's delta-time is above this, we should update the tempo.
			self.tempo = self.tempoList[1]

			sustainEvents = len(self.sustainList) / 2
			i = 0

			while (i < sustainEvents):
				sustainDelta = self.sustainList[i * 2]
				if not (reachedEndOfTempoChanges) and (sustainDelta >= nextTempoDelta):
					if(tempoIndex < numOfTempoChanges - 2):
						tempoIndex += 1

						self.tempo = self.tempoList[((tempoIndex) * 2) + 1]
						currentTempoBlockMS = self.tempoBlock[tempoIndex - 1]

						currentTempoDelta = nextTempoDelta
						nextTempoDelta = self.tempoList[(tempoIndex + 1) * 2]

					else: # Reached the end of the tempoBlockList.
						reachedEndOfTempoChanges = True

				deltaRelativeToTempo = sustainDelta - currentTempoDelta # This will let us figure out how long it's been since the last tempo change.
				realMS = self.deltaTimeToMS(deltaRelativeToTempo) + currentTempoBlockMS # This should get an accurate millisecond value.

				self.sustainList[i * 2] = realMS
				i += 1

			# Key press data.
			i = 0
			while (i < self.keyNum):
				tempoIndex = 0  # This is going to be used to iterate through the tempo blocks.
				reachedEndOfTempoChanges = False
				currentTempoBlockMS = 0  # The value we'll fetch from the tempo block. Should start as 0.
				currentTempoDelta = 0  # The delta-time of the current tempo change. Used to calculate the difference between the last tempo block, and the current event
				nextTempoDelta = self.tempoList[2]  # The delta-time of the next tempo change. If our event's delta-time is above this, we should update the tempo.
				self.tempo = self.tempoList[1]

				j = 0
				thisKeyEvents = len(self.keyPresses[i]) / 3  # This is how many times this particular key was pressed. As we store 3 pieces of data per entry, we need to divide by 3 to find out how many events there are.

				while (j < thisKeyEvents):
					keyDelta = self.keyPresses[i][j * 3]
					if not (reachedEndOfTempoChanges) and (keyDelta >= nextTempoDelta):
						if (tempoIndex < numOfTempoChanges - 2):
							tempoIndex += 1

							self.tempo = self.tempoList[((tempoIndex) * 2) + 1]
							currentTempoBlockMS = self.tempoBlock[tempoIndex - 1]

							currentTempoDelta = nextTempoDelta
							nextTempoDelta = self.tempoList[(tempoIndex + 1) * 2]

						else:  # Reached the end of the tempoBlockList.
							reachedEndOfTempoChanges = True

					deltaRelativeToTempo = keyDelta - currentTempoDelta  # This will let us figure out how long it's been since the last tempo change.
					realMS = self.deltaTimeToMS(deltaRelativeToTempo) + currentTempoBlockMS  # This should get an accurate millisecond value.

					self.keyPresses[i][j * 3] = realMS
					j += 1
				i += 1


		else: # If there's only 1 tempo through the whole song, we can simply convert the delta times directly.

			# Sustain pedal data.
			sustainEvents = len(self.sustainList) / 2
			i = 0
			while(i < sustainEvents):
				self.sustainList[i * 2] = self.deltaTimeToMS(self.sustainList[i * 2])
				i += 1

			# Key press data.
			i = 0
			while(i < self.keyNum):
				j = 0
				thisKeyEvents = len(self.keyPresses[i]) / 3 # This is how many times this particular key was pressed. As we store 3 pieces of data per entry, we need to divide by 3 to find out how many events there are.
				while(j < thisKeyEvents):
					self.keyPresses[i][j * 3] = self.deltaTimeToMS(self.keyPresses[i][j * 3])
					j += 1
				i += 1

	def animateKeys(self):
		if(self.errTriggered):
			return()


		for i in range(self.keyNum): # For each key in that we've kept data on...
			activeKeyData = self.keyPresses[i]
			keyEvents = int(len(activeKeyData) / 3) # This will tells us how many times the key is pressed or released. As each event has 3 pieces of data, we divide by 3 to get the real number.
			activeKeyObject = self.objectList[i]

			for j in range(keyEvents): # For each event related to this pitch...
				eventIndex = j * 3

				targetFrame = (activeKeyData[eventIndex] // self.millisecondsPerFrame) + self.frameStart
				isOn = activeKeyData[eventIndex + 1] # Was the key pressed (True) or released (False)
				velocity = activeKeyData[eventIndex + 2] # How fast the key was pressed.

				velocityPercentage = velocity / 127 # This will calculate the percentage of its maximum velocity has. At 0, it will have the maximum velocity offset.
				try:
					frameOffset = self.velocityOffset / velocityPercentage # How many frames it should take for the key to reach its destination
				except ZeroDivisionError:
					frameOffset = 0

				if(isOn):
					# Start frame
					startFrame = (targetFrame - self.pressTime)
					# We won't set a position for the start angle, as it should be relative to the current position.
					activeKeyObject.keyframe_insert(data_path = "rotation_euler", frame = startFrame, index = 0)

					# End frame
					endFrame = targetFrame
					activeKeyObject.rotation_euler[0] = self.keyAngle
					activeKeyObject.keyframe_insert(data_path = "rotation_euler", frame = endFrame, index = 0)
				else:
					# Start frame
					startFrame = (targetFrame - self.releaseTime)
					# We won't set a position for the start angle, as it should be relative to the current position.
					activeKeyObject.keyframe_insert(data_path = "rotation_euler", frame = startFrame, index = 0)

					# End frame
					endFrame = targetFrame
					activeKeyObject.rotation_euler[0] = 0
					activeKeyObject.keyframe_insert(data_path = "rotation_euler", frame = endFrame, index = 0)

				# Set F-Curves of key
				fc = activeKeyObject.animation_data.action.fcurves
				targetFC = fc.find("rotation_euler", index = 0)
				targetFC.keyframe_points[-2].interpolation = "LINEAR"
				targetFC.keyframe_points[-1].interpolation = "LINEAR"



	def pickFromArray(self, parseAmount, offset, array):
		"""
		This is just a debug thing. It will take every entry at a multiple of X from an array, and create a new array out of it.
		As I store much of my data as [var0.0, var0.1, var0.2, var1.0, var1.1, var1.2...], printing just one "type" of data from these arrays require special parsing.
		"""

		arrlen = len(array) / parseAmount
		newArray = [None for i in range(arrlen)] # Create an empty array of arrlen length.

		i = 0
		while(i < arrlen):
			newArray[i] = array[(i * parseAmount) + offset]
			i += 1

		return(newArray)


class FileManager():
	"""
	This object is designed to make it easier for me to interact with the data that's read from a binary file.
	It simply stores the different formats I might want to read the data in.
	Note that I am not checking for errTriggered in here for efficiency. Try not to trigger an error and then call anything in this object :P
	"""
	def __init__(self):
		self.file = 0
		self.savedB = b'' # The value stored as Python's weird b value.
		self.savedInt = 0
		self.savedAscii = ""
		self.intRead = False # If the int has been called and there is no new data, just return the last thing we decoded. Optimization (I hope)
		self.asciiRead = False

	def read(self, bytes, outputType = 0):
		"""
		:param bytes: How many bytes to read
		:param outputType: The data type to be outputted by this function. This is simply a shortcut, instead of reading and then converting to int, I can simply return the int immediately. Optional argument.
		:return:
		"""
		self.savedB = self.file.read(bytes)
		self.intRead = False
		self.asciiRead = False

		if(outputType == 0):
			return self.savedB

		elif(outputType == 1):
			return self.asInt()

		elif(outputType == 2):
			return self.asAscii()

	def skip(self, bytes):
		"""Skips past the given amount of bytes by setting a new seek position. Seeks relative to the current position."""
		self.file.seek(bytes, 1)
		pass

	def asInt(self):
		if not self.intRead:
			self.savedInt = int.from_bytes(self.savedB, byteorder = "big", signed = False)
			return self.savedInt
		else:
			return self.savedInt

	def asAscii(self):
		if not self.asciiRead:
			try:
				self.savedAscii = self.savedB.decode("ascii")
				self.asciiRead = True
				return self.savedAscii
			except UnicodeDecodeError:
				print("Minor error: Tried to decode a value into ascii above 127. May signify that buffer seek position is misplaced.")
				self.savedAscii = ""
				self.asciiRead = True
				return self.savedAscii
			except Exception as e:
				print("Unexpected error encountered while decoding asAscii: " + str(e))

		else:
			return self.savedAscii


pn = PianoPlay() # This just calls the above class.
print(pn.keyPresses[50])

# Design ideas. These are things I want to add in the future.
#
# Allow users to create an animation action, and use that on the keys.
# Support for instruments other pianos might be a long way off, but if people request it I'll look into it.
# Allow keys to light up in colour when pressed.
# Support for other formats? I don't know any others right now, but maybe I could make a custom one in the future?
# Maybe start using dictionaries when searching for things such as metaevent tags.
# Add multi track support, so a user can specify two pianos or instruments or whatever.
# Test whether doing two passes on the midi file to figure out list size will be faster than appending the data to the lists.
# Remake code to be less... bad.
# Rotate keys based on Z axis down, rather than my current system (Euler X)


# Some notes I want to make about the system I'm using.
# Right now, because I hand make the animations, they won't really work in any setting besides the one that I've defined.
# Because of this, I'm also *setting* the angle that a key plays at, instead of moving it relative to its current position. This will absolutely cause problems if the instrument is rotated at all.
#
# Really need to find a way to avoid using fc.find in my code. Animating via python code in Blender is a huge pain in the ass, so I just took the first answer I found in this case.


# To do next time:
# For some reason the millisecond times of key presses are getting wildly large gaps between them. This signifies there's an error in how I'm calculating them. I'll need to look into this.
# Note on above. Further investigation reveals a pattern that looks like it has to do with how I'm decoding the variable-length values. Further testing required.































