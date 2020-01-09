# by amounra 0216 : http://www.aumhaa.com
# written against Live 9.6 release on 021516


from ableton.v2.control_surface.elements.color import Color
from aumhaa.v2.livid.colors import *

"""
Ohm64_Map.py

Created by amounra on 2010-10-05.
Copyright (c) 2010 __artisia__. All rights reserved.

This file allows the reassignment of the controls from their default arrangement.  The order is from left to right;
Buttons are Note #'s and Faders/Rotaries are Controller #'s

"""
CHANNEL = 0		#main channel (0 - 15)

FADER_BANKING = False

DIAL_BANKING = False

USER_CHANNEL = 8

OHM_BUTTONS = [65, 73, 66, 74, 67, 75, 68, 76]    #there are 8 of these

OHM_FADERS = [23, 22, 15, 14, 5, 7, 6, 4]		#there are 8 of these

OHM_DIALS = [17, 16, 9, 8, 19, 18, 11, 10, 21, 20, 13, 12, 3, 1, 0, 2]		#there are 16 of these

OHM_MENU = [69, 70, 71, 77, 78, 79]			#there are 6 of these

CROSSFADER = 24		#single

SHIFT_L = 64		#single

SHIFT_R = 72		#single

LIVID = 87			#single

PAGE1_DRUM_CHANNEL = 9			#this is the channel for the first (partial right) grid in Right Function Mode 2

PAGE1_DRUM_MAP = 	[[0, 1, 2, 3],			#these are the note numbers for the first (partial) grid in Right Function Mode 2
 					[4, 5, 6, 7],
					[8, 9, 10, 11],
					[12, 13, 14, 15]]

PAGE1_BASS_CHANNEL = 10			#this is the channel for the second (full right) grid in Right Function Modes 3 & 4

PAGE1_BASS_MAP = 	[[24, 28, 32, 36],		#these are the note numbers for the first (partial) grid in Right Function Mode 3 & 4
					[25, 29, 33, 37],
					[26, 30, 34, 38],
					[27, 31, 35, 39]]

PAGE1_KEYS_CHANNEL = 11

PAGE1_KEYS_MAP =   [[24, 12, 0],
					[26, 14, 2],
					[28, 16, 4],
					[29, 17, 5],
					[31, 19, 7],
					[33, 21, 9],
					[35, 23, 11],
					[36, 24, 12]]

PAGE1_MODES_MAP = [[0, 0, 0, 0, 0, 0, 0, 0], #major or ionian
					[0, 0, -1, 0, 0, 0, -1, 0], #dorian
					[0, -1, -1, 0, 0, -1, -1, 0], #phrygian
					[0, 0, 0, 1, 0, 0, 0, 0],  #lydian
					[0, 0, 0, 0, 0, 0, -1, 0], #mixolydian
					[0, 0, -1, 0, 0, -1, -1, 0], #minor or aeolian
					[0, -1, -1, 0, -1, -1, -1, 0], #locrian
					[0, 0, 0, 0, 0, 0, 0, 0]]


BACKLIGHT_TYPE = ['static', 'pulse', 'up', 'down']  #this assigns the backlight mode for left_shift_modes 1-4.  If 'static', the value below will be used

BACKLIGHT_VALUE = [127, 96, 64, 32]		#this assigns the led intensity for the backlight if it is in 'static' mode for left_shift_modes 1-4

OHM_TYPE = ['static', 'pulse', 'up', 'down']	#this assigns the ohm logo mode for right_shift_modes 1-4.  If 'static', the value below will be used

OHM_VALUE = [127, 96, 64, 32]	#this assigns the led intensity for the ohm logo if it is in 'static' mode for right_shift_modes 1-4

PAD_TRANSLATION = 	((0, 0, 0, 9), (0, 1, 1, 9), (0, 2, 2, 9), (0, 3, 3, 9),		#this is used by DrumRacks to translate input to one of the visible grid squares for triggering
					(1, 0, 4, 9), (1, 1, 5, 9), (1, 2, 6, 9), (1, 3, 7, 9),			#the format is (x position, y position, note-number, channel)
					(2, 0, 8, 9), (2, 1, 9, 9), (2, 2, 10, 9), (2, 3, 11, 9),
					(3, 0, 12, 9), (3, 1, 13, 9), (3, 2, 14, 9), (3, 3, 15, 9))



FOLLOW = True		#this sets whether or not the last selected device on a track is selected for editing when you select a new track


LENGTH_VALUES = [2, 3, 4]

CHANNELS = ['Ch. 2', 'Ch. 3', 'Ch. 4', 'Ch. 5', 'Ch. 6', 'Ch. 7', 'Ch. 8', 'Ch. 9', 'Ch. 10', 'Ch. 11', 'Ch. 12', 'Ch. 13', 'Ch. 14']

"""These are the scales we have available.  You can freely add your own scales to this """
SCALES = 	{'Mod':[0,1,2,3,4,5,6,7,8,9,10,11],
			'Session':[0,1,2,3,4,5,6,7,8,9,10,11],
			'Keys':[0,2,4,5,7,9,11,12,1,3,3,6,8,10,10,13],
			'Auto':[0,1,2,3,4,5,6,7,8,9,10,11],
			'Chromatic':[0,1,2,3,4,5,6,7,8,9,10,11],
			'DrumPad':[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
			'Major':[0,2,4,5,7,9,11],
			'Minor':[0,2,3,5,7,8,10],
			'Dorian':[0,2,3,5,7,9,10],
			'Mixolydian':[0,2,4,5,7,9,10],
			'Lydian':[0,2,4,6,7,9,11],
			'Phrygian':[0,1,3,5,7,8,10],
			'Locrian':[0,1,3,4,7,8,10],
			'Diminished':[0,1,3,4,6,7,9,10],
			'Whole-half':[0,2,3,5,6,8,9,11],
			'Whole_Tone':[0,2,4,6,8,10],
			'Minor_Blues':[0,3,5,6,7,10],
			'Minor_Pentatonic':[0,3,5,7,10],
			'Major_Pentatonic':[0,2,4,7,9],
			'Harmonic_Minor':[0,2,3,5,7,8,11],
			'Melodic_Minor':[0,2,3,5,7,9,11],
			'Dominant_Sus':[0,2,5,7,9,10],
			'Super_Locrian':[0,1,3,4,6,8,10],
			'Neopolitan_Minor':[0,1,3,5,7,8,11],
			'Neopolitan_Major':[0,1,3,5,7,9,11],
			'Enigmatic_Minor':[0,1,3,6,7,10,11],
			'Enigmatic':[0,1,4,6,8,10,11],
			'Composite':[0,1,4,6,7,8,11],
			'Bebop_Locrian':[0,2,3,5,6,8,10,11],
			'Bebop_Dominant':[0,2,4,5,7,9,10,11],
			'Bebop_Major':[0,2,4,5,7,8,9,11],
			'Bhairav':[0,1,4,5,7,8,11],
			'Hungarian_Minor':[0,2,3,6,7,8,11],
			'Minor_Gypsy':[0,1,4,5,7,8,10],
			'Persian':[0,1,4,5,6,8,11],
			'Hirojoshi':[0,2,3,7,8],
			'In-Sen':[0,1,5,7,10],
			'Iwato':[0,1,5,6,10],
			'Kumoi':[0,2,3,7,9],
			'Pelog':[0,1,3,4,7,8],
			'Spanish':[0,1,3,4,5,6,8,10]
			}

SCALEABBREVS = {'Auto':'-A','Keys':'-K','Chromatic':'12','DrumPad':'-D','Major':'M-','Minor':'m-','Dorian':'II','Mixolydian':'V',
			'Lydian':'IV','Phrygian':'IH','Locrian':'VH','Diminished':'d-','Whole-half':'Wh','Whole_Tone':'WT','Minor_Blues':'mB',
			'Minor_Pentatonic':'mP','Major_Pentatonic':'MP','Harmonic_Minor':'mH','Melodic_Minor':'mM','Dominant_Sus':'D+','Super_Locrian':'SL',
			'Neopolitan_Minor':'mN','Neopolitan_Major':'MN','Enigmatic_Minor':'mE','Enigmatic':'ME','Composite':'Cp','Bebop_Locrian':'lB',
			'Bebop_Dominant':'DB','Bebop_Major':'MB','Bhairav':'Bv','Hungarian_Minor':'mH','Minor_Gypsy':'mG','Persian':'Pr',
			'Hirojoshi':'Hr','In-Sen':'IS','Iwato':'Iw','Kumoi':'Km','Pelog':'Pg','Spanish':'Sp'}


"""This is the default scale used by Auto when something other than a drumrack is detected for the selected track"""
DEFAULT_AUTO_SCALE = 'Major'

"""This is the default Vertical Offset for any scale other than DrumPad """
DEFAULT_VERTOFFSET = 4

"""This is the default NoteOffset, aka RootNote, used for scales other than DrumPad"""
DEFAULT_OFFSET = 48

"""This is the default NoteOffset, aka RootNote, used for the DrumPad scale;  it is a multiple of 4, so an offset of 4 is actually a RootNote of 16"""
DEFAULT_DRUMOFFSET = 9

"""This is the default Scale used for all MIDI Channels"""
DEFAULT_SCALE = 'Auto'

"""This is the default SplitMode used for all MIDI Channels"""
DEFAULT_MODE = 'seq'

SCALENAMES = [scale for scale in sorted(SCALES.iterkeys())]

"""It is possible to create a custom list of scales to be used by the script.  For instance, the list below would include major, minor, auto, drumpad, and chromatic scales, in that order."""
#SCALENAMES = ['Major', 'Minor', 'Auto', 'DrumPad', 'Chromatic']

DEFAULT_INSTRUMENT_SETTINGS = {'Scales':SCALES,
								'ScaleAbbrevs':SCALEABBREVS,
								'ScaleNames':SCALENAMES,
								'DefaultAutoScale':DEFAULT_AUTO_SCALE,
								'DefaultVertOffset':DEFAULT_VERTOFFSET,
								'DefaultOffset':DEFAULT_OFFSET,
								'DefaultDrumOffset':DEFAULT_DRUMOFFSET,
								'DefaultScale':DEFAULT_SCALE,
								'DefaultMode':DEFAULT_MODE,
								'Channels':CHANNELS}


#	The default assignment of colors within the OhmRGB is:
#	Note 2 = white
#	Note 4 = cyan
#	Note 8 = magenta
#	Note 16 = red
#	Note 32 = blue
#	Note 64 = yellow
#	Note 127 = green
#	Because the colors are reassignable, and the default colors have changed from the initial prototype,
#		MonOhm script utilizes a color map to assign colors to the buttons.  This color map can be changed
#		here in the script.  The color ordering is from 1 to 7.

#Colors = [white, yellow, cyan, magenta, red, green, blue]
COLOR_MAP = [2, 64, 4, 8, 16, 127, 32]

#	In addition, there are two further color maps that are used depending on whether the RGB or Monochrome
#		Ohm64 is detected.  The second number is the color used by the RGB (from the ordering in the COLOR_MAP array),
#		the first the Monochrome.  Obviously the Monochrome doesn't use the colors.
#	However, the flashing status of a color is derived at by modulus.  Thus 1-6 are the raw colors, 7-12 are a fast
#		flashing color, 13-20 flash a little slower, etc.  127 is always solid.  You can assign your own color maps here:


STOP_CLIP_COLOR = [127, 1]
CLIP_TRIGD_TO_PLAY_COLOR = [13, 1]
CLIP_TRIGD_TO_RECORD_COLOR = [12, 1]
CLIP_STOPPED_COLOR = [1, 1]
CLIP_STARTED_COLOR = [6, 13]
CLIP_RECORDING_COLOR = [5, 19]
ZOOM_STOPPED_COLOR = [1, 1]
ZOOM_PLAYING_COLOR = [6, 13]
ZOOM_SELECTED_COLOR = [9, 7]


ARM_COLOR = [5, 14]
STOP_COLOR = [127, 1]
PLAY_COLOR = [6, 1]
MUTE_COLOR = [2, 1]
CROSSFADE_ASSIGN_COLOR = [4, 1]
SCENE_LAUNCH_COLOR = [1, 7]
NAV_BUTTON_COLOR = [3, 1]
DRUM_COLOR = [6, 20]
KEYS_COLOR = [2, 1]
BASS_COLOR = [5, 32]
DEVICE_NAV_COLOR = [2, 1]
SOLO_COLOR = [3, 7]
TAP_COLOR = [1, 1]
SELECT_COLOR = [1, 127]


class OhmColors:


	class DefaultButton:
		On = LividRGB.WHITE
		Off = LividRGB.OFF
		Disabled = LividRGB.OFF
		Alert = LividRGB.BlinkFast.WHITE


	class MainModes:
		Clips = LividRGB.WHITE
		Clips_shifted = LividRGB.BlinkFast.WHITE
		Sends = LividRGB.MAGENTA
		Sends_shifted = LividRGB.BlinkFast.MAGENTA
		Device = LividRGB.CYAN
		Device_shifted = LividRGB.BlinkFast.CYAN
		User = LividRGB.RED
		User_shifted = LividRGB.BlinkFast.RED


	class Session:
		StopClipTriggered = LividRGB.BlinkFast.BLUE
		StopClip = LividRGB.BLUE
		Scene = LividRGB.CYAN
		NoScene = LividRGB.OFF
		SceneTriggered = LividRGB.BlinkFast.BLUE
		ClipTriggeredPlay = LividRGB.BlinkFast.GREEN
		ClipTriggeredRecord = LividRGB.BlinkFast.RED
		RecordButton = LividRGB.OFF
		ClipEmpty = LividRGB.OFF
		ClipStopped = LividRGB.WHITE
		ClipStarted = LividRGB.GREEN
		ClipRecording = LividRGB.RED
		NavigationButtonOn = LividRGB.MAGENTA
		PageNavigationButtonOn = LividRGB.CYAN
		Empty = LividRGB.OFF


	class Zooming:
		Selected = LividRGB.BlinkFast.YELLOW
		Stopped = LividRGB.WHITE
		Playing = LividRGB.GREEN
		Empty = LividRGB.OFF


	class LoopSelector:
		Playhead = LividRGB.YELLOW
		PlayheadRecord = LividRGB.YELLOW
		OutsideLoop = LividRGB.BLUE
		InsideLoopStartBar = LividRGB.CYAN
		SelectedPage = LividRGB.WHITE
		InsideLoop = LividRGB.CYAN
		PlayheadRecord = LividRGB.RED


	class NoteEditor:

		class Step:
			Low = LividRGB.CYAN
			High = LividRGB.WHITE
			Full = LividRGB.YELLOW
			Muted = LividRGB.YELLOW
			StepEmpty = LividRGB.OFF


		class StepEditing:
			High = LividRGB.GREEN
			Low = LividRGB.CYAN
			Full = LividRGB.YELLOW
			Muted = LividRGB.WHITE


		StepEmpty = LividRGB.OFF
		StepEmptyBase = LividRGB.OFF
		StepEmptyScale = LividRGB.OFF
		StepDisabled = LividRGB.OFF
		Playhead = Color(127)
		PlayheadRecord = Color(31)
		StepSelected = LividRGB.GREEN
		QuantizationSelected = LividRGB.RED
		QuantizationUnselected = LividRGB.MAGENTA


	class DrumGroup:
		#PadAction = LividRGB.WHITE
		PadFilled = LividRGB.GREEN
		PadFilledAlt = LividRGB.MAGENTA
		PadSelected = LividRGB.BlinkFast.WHITE
		PadSelectedNotSoloed = LividRGB.BlinkFast.WHITE
		PadEmpty = LividRGB.OFF
		PadMuted = LividRGB.YELLOW
		PadSoloed = LividRGB.BLUE
		PadMutedSelected = LividRGB.BlinkFast.YELLOW
		PadSoloedSelected = LividRGB.BlinkFast.BLUE
		PadInvisible = LividRGB.OFF
		PadAction = LividRGB.RED


	class Mixer:
		SoloOn = LividRGB.BlinkFast.CYAN
		SoloOff = LividRGB.OFF
		MuteOn = LividRGB.YELLOW
		MuteOff = LividRGB.OFF
		ArmSelected = LividRGB.GREEN
		ArmUnselected = LividRGB.RED
		ArmOff = LividRGB.OFF
		StopClip = LividRGB.BLUE
		SelectedOn = LividRGB.BLUE
		SelectedOff = LividRGB.OFF
		XFadeOff = LividRGB.OFF
		XFadeAOn = LividRGB.YELLOW
		XFadeBOn = LividRGB.MAGENTA


	class Recording:
		On = LividRGB.BlinkFast.GREEN
		Off = LividRGB.GREEN
		Transition = LividRGB.BlinkSlow.GREEN


	class Recorder:
		On = LividRGB.WHITE
		Off = LividRGB.BLUE
		NewOn = LividRGB.BlinkFast.YELLOW
		NewOff = LividRGB.YELLOW
		FixedOn = LividRGB.BlinkFast.CYAN
		FixedOff = LividRGB.CYAN
		RecordOn = LividRGB.BlinkFast.GREEN
		RecordOff = LividRGB.GREEN
		FixedAssigned = LividRGB.MAGENTA
		FixedNotAssigned = LividRGB.OFF
		OverdubOn = LividRGB.BlinkFast.RED
		OverdubOff = LividRGB.RED


	class Transport:
		OverdubOn = LividRGB.BlinkFast.RED
		OverdubOff = LividRGB.RED
		PlayOn = LividRGB.BlinkSlow.GREEN
		PlayOff = LividRGB.GREEN
		StopOn = LividRGB.BLUE
		StopOff = LividRGB.BLUE


	class Device:
		NavOn = LividRGB.MAGENTA
		NavOff = LividRGB.OFF
		BankOn = LividRGB.YELLOW
		BankOff = LividRGB.OFF
		ChainNavOn = LividRGB.RED
		ChainNavOff = LividRGB.OFF
		ContainNavOn = LividRGB.CYAN
		ContainNavOff = LividRGB.OFF


	class DeviceNavigator:
		DevNavOff = LividRGB.OFF
		DevNavOn = LividRGB.MAGENTA
		ChainNavOn = LividRGB.RED
		ChainNavOff = LividRGB.OFF
		LevelNavOn = LividRGB.CYAN
		LevelNavOff = LividRGB.OFF


	class Mod:
		class Nav:
			OnValue = LividRGB.RED
			OffValue = LividRGB.WHITE



	class MonoInstrument:

		PressFlash = LividRGB.WHITE
		OffsetOnValue = LividRGB.GREEN
		OffsetOffValue = LividRGB.OFF
		ScaleOffsetOnValue = LividRGB.RED
		ScaleOffsetOffValue = LividRGB.OFF
		SplitModeOnValue = LividRGB.WHITE
		SplitModeOffValue = LividRGB.OFF
		SequencerModeOnValue = LividRGB.CYAN
		SequencerModeOffValue = LividRGB.OFF
		DrumOffsetOnValue = LividRGB.MAGENTA
		DrumOffsetOffValue = LividRGB.OFF
		VerticalOffsetOnValue = LividRGB.BLUE
		VerticalOffsetOffValue = LividRGB.OFF
		OffsetOnColor = LividRGB.YELLOW
		OffsetOffColor = LividRGB.OFF

		class Keys:
			SelectedNote = LividRGB.GREEN
			RootWhiteValue = LividRGB.RED
			RootBlackValue = LividRGB.MAGENTA
			WhiteValue = LividRGB.CYAN
			BlackValue = LividRGB.BLUE
			OnValue = LividRGB.YELLOW


		class Drums:
			SelectedNote = LividRGB.GREEN
			EvenValue = LividRGB.GREEN
			OddValue = LividRGB.GREEN


		class Bass:
			OnValue = LividRGB.RED


	class Translation:

		SelectorOn = LividRGB.WHITE
		SelectorOff = LividRGB.OFF


		class Channel_8:
			Grid_0 = LividRGB.OFF
			Grid_1 = LividRGB.OFF
			Grid_2 = LividRGB.OFF
			Grid_3 = LividRGB.OFF
			Grid_4 = LividRGB.OFF
			Grid_5 = LividRGB.OFF
			Grid_6 = LividRGB.OFF
			Grid_7 = LividRGB.OFF
			Grid_8 = LividRGB.OFF
			Grid_9 = LividRGB.OFF
			Grid_10 = LividRGB.OFF
			Grid_11 = LividRGB.OFF
			Grid_12 = LividRGB.OFF
			Grid_13 = LividRGB.OFF
			Grid_14 = LividRGB.OFF
			Grid_15 = LividRGB.OFF
			Grid_16 = LividRGB.OFF
			Grid_17 = LividRGB.OFF
			Grid_18 = LividRGB.OFF
			Grid_19 = LividRGB.OFF
			Grid_20 = LividRGB.OFF
			Grid_21 = LividRGB.OFF
			Grid_22 = LividRGB.OFF
			Grid_23 = LividRGB.OFF
			Grid_24 = LividRGB.OFF
			Grid_25 = LividRGB.OFF
			Grid_26 = LividRGB.OFF
			Grid_27 = LividRGB.OFF
			Grid_28 = LividRGB.OFF
			Grid_29 = LividRGB.OFF
			Grid_30 = LividRGB.OFF
			Grid_31 = LividRGB.OFF
			Grid_32 = LividRGB.OFF
			Grid_33 = LividRGB.OFF
			Grid_34 = LividRGB.OFF
			Grid_35 = LividRGB.OFF
			Grid_36 = LividRGB.OFF
			Grid_37 = LividRGB.OFF
			Grid_38 = LividRGB.OFF
			Grid_39 = LividRGB.OFF
			Grid_40 = LividRGB.OFF
			Grid_41 = LividRGB.OFF
			Grid_42 = LividRGB.OFF
			Grid_43 = LividRGB.OFF
			Grid_44 = LividRGB.OFF
			Grid_45 = LividRGB.OFF
			Grid_46 = LividRGB.OFF
			Grid_47 = LividRGB.OFF
			Grid_48 = LividRGB.OFF
			Grid_49 = LividRGB.OFF
			Grid_50 = LividRGB.OFF
			Grid_51 = LividRGB.OFF
			Grid_52 = LividRGB.OFF
			Grid_53 = LividRGB.OFF
			Grid_54 = LividRGB.OFF
			Grid_55 = LividRGB.OFF
			Grid_56 = LividRGB.OFF
			Grid_57 = LividRGB.OFF
			Grid_58 = LividRGB.OFF
			Grid_59 = LividRGB.OFF
			Grid_60 = LividRGB.OFF
			Grid_61 = LividRGB.OFF
			Grid_62 = LividRGB.OFF
			Grid_63 = LividRGB.OFF


		class Channel_9:
			Grid_0 = LividRGB.OFF
			Grid_1 = LividRGB.OFF
			Grid_2 = LividRGB.OFF
			Grid_3 = LividRGB.OFF
			Grid_4 = LividRGB.OFF
			Grid_5 = LividRGB.OFF
			Grid_6 = LividRGB.OFF
			Grid_7 = LividRGB.OFF
			Grid_8 = LividRGB.OFF
			Grid_9 = LividRGB.OFF
			Grid_10 = LividRGB.OFF
			Grid_11 = LividRGB.OFF
			Grid_12 = LividRGB.OFF
			Grid_13 = LividRGB.OFF
			Grid_14 = LividRGB.OFF
			Grid_15 = LividRGB.OFF
			Grid_16 = LividRGB.OFF
			Grid_17 = LividRGB.OFF
			Grid_18 = LividRGB.OFF
			Grid_19 = LividRGB.OFF
			Grid_20 = LividRGB.OFF
			Grid_21 = LividRGB.OFF
			Grid_22 = LividRGB.OFF
			Grid_23 = LividRGB.OFF
			Grid_24 = LividRGB.OFF
			Grid_25 = LividRGB.OFF
			Grid_26 = LividRGB.OFF
			Grid_27 = LividRGB.OFF
			Grid_28 = LividRGB.OFF
			Grid_29 = LividRGB.OFF
			Grid_30 = LividRGB.OFF
			Grid_31 = LividRGB.OFF
			Grid_32 = LividRGB.OFF
			Grid_33 = LividRGB.OFF
			Grid_34 = LividRGB.OFF
			Grid_35 = LividRGB.OFF
			Grid_36 = LividRGB.OFF
			Grid_37 = LividRGB.OFF
			Grid_38 = LividRGB.OFF
			Grid_39 = LividRGB.OFF
			Grid_40 = LividRGB.OFF
			Grid_41 = LividRGB.OFF
			Grid_42 = LividRGB.OFF
			Grid_43 = LividRGB.OFF
			Grid_44 = LividRGB.OFF
			Grid_45 = LividRGB.OFF
			Grid_46 = LividRGB.OFF
			Grid_47 = LividRGB.OFF
			Grid_48 = LividRGB.OFF
			Grid_49 = LividRGB.OFF
			Grid_50 = LividRGB.OFF
			Grid_51 = LividRGB.OFF
			Grid_52 = LividRGB.OFF
			Grid_53 = LividRGB.OFF
			Grid_54 = LividRGB.OFF
			Grid_55 = LividRGB.OFF
			Grid_56 = LividRGB.OFF
			Grid_57 = LividRGB.OFF
			Grid_58 = LividRGB.OFF
			Grid_59 = LividRGB.OFF
			Grid_60 = LividRGB.OFF
			Grid_61 = LividRGB.OFF
			Grid_62 = LividRGB.OFF
			Grid_63 = LividRGB.OFF

		class Channel_10:
			Grid_0 = LividRGB.OFF
			Grid_1 = LividRGB.OFF
			Grid_2 = LividRGB.OFF
			Grid_3 = LividRGB.OFF
			Grid_4 = LividRGB.OFF
			Grid_5 = LividRGB.OFF
			Grid_6 = LividRGB.OFF
			Grid_7 = LividRGB.OFF
			Grid_8 = LividRGB.OFF
			Grid_9 = LividRGB.OFF
			Grid_10 = LividRGB.OFF
			Grid_11 = LividRGB.OFF
			Grid_12 = LividRGB.OFF
			Grid_13 = LividRGB.OFF
			Grid_14 = LividRGB.OFF
			Grid_15 = LividRGB.OFF
			Grid_16 = LividRGB.OFF
			Grid_17 = LividRGB.OFF
			Grid_18 = LividRGB.OFF
			Grid_19 = LividRGB.OFF
			Grid_20 = LividRGB.OFF
			Grid_21 = LividRGB.OFF
			Grid_22 = LividRGB.OFF
			Grid_23 = LividRGB.OFF
			Grid_24 = LividRGB.OFF
			Grid_25 = LividRGB.OFF
			Grid_26 = LividRGB.OFF
			Grid_27 = LividRGB.OFF
			Grid_28 = LividRGB.OFF
			Grid_29 = LividRGB.OFF
			Grid_30 = LividRGB.OFF
			Grid_31 = LividRGB.OFF
			Grid_32 = LividRGB.OFF
			Grid_33 = LividRGB.OFF
			Grid_34 = LividRGB.OFF
			Grid_35 = LividRGB.OFF
			Grid_36 = LividRGB.OFF
			Grid_37 = LividRGB.OFF
			Grid_38 = LividRGB.OFF
			Grid_39 = LividRGB.OFF
			Grid_40 = LividRGB.OFF
			Grid_41 = LividRGB.OFF
			Grid_42 = LividRGB.OFF
			Grid_43 = LividRGB.OFF
			Grid_44 = LividRGB.OFF
			Grid_45 = LividRGB.OFF
			Grid_46 = LividRGB.OFF
			Grid_47 = LividRGB.OFF
			Grid_48 = LividRGB.OFF
			Grid_49 = LividRGB.OFF
			Grid_50 = LividRGB.OFF
			Grid_51 = LividRGB.OFF
			Grid_52 = LividRGB.OFF
			Grid_53 = LividRGB.OFF
			Grid_54 = LividRGB.OFF
			Grid_55 = LividRGB.OFF
			Grid_56 = LividRGB.OFF
			Grid_57 = LividRGB.OFF
			Grid_58 = LividRGB.OFF
			Grid_59 = LividRGB.OFF
			Grid_60 = LividRGB.OFF
			Grid_61 = LividRGB.OFF
			Grid_62 = LividRGB.OFF
			Grid_63 = LividRGB.OFF

		class Channel_11:
			Grid_0 = LividRGB.OFF
			Grid_1 = LividRGB.OFF
			Grid_2 = LividRGB.OFF
			Grid_3 = LividRGB.OFF
			Grid_4 = LividRGB.OFF
			Grid_5 = LividRGB.OFF
			Grid_6 = LividRGB.OFF
			Grid_7 = LividRGB.OFF
			Grid_8 = LividRGB.OFF
			Grid_9 = LividRGB.OFF
			Grid_10 = LividRGB.OFF
			Grid_11 = LividRGB.OFF
			Grid_12 = LividRGB.OFF
			Grid_13 = LividRGB.OFF
			Grid_14 = LividRGB.OFF
			Grid_15 = LividRGB.OFF
			Grid_16 = LividRGB.OFF
			Grid_17 = LividRGB.OFF
			Grid_18 = LividRGB.OFF
			Grid_19 = LividRGB.OFF
			Grid_20 = LividRGB.OFF
			Grid_21 = LividRGB.OFF
			Grid_22 = LividRGB.OFF
			Grid_23 = LividRGB.OFF
			Grid_24 = LividRGB.OFF
			Grid_25 = LividRGB.OFF
			Grid_26 = LividRGB.OFF
			Grid_27 = LividRGB.OFF
			Grid_28 = LividRGB.OFF
			Grid_29 = LividRGB.OFF
			Grid_30 = LividRGB.OFF
			Grid_31 = LividRGB.OFF
			Grid_32 = LividRGB.OFF
			Grid_33 = LividRGB.OFF
			Grid_34 = LividRGB.OFF
			Grid_35 = LividRGB.OFF
			Grid_36 = LividRGB.OFF
			Grid_37 = LividRGB.OFF
			Grid_38 = LividRGB.OFF
			Grid_39 = LividRGB.OFF
			Grid_40 = LividRGB.OFF
			Grid_41 = LividRGB.OFF
			Grid_42 = LividRGB.OFF
			Grid_43 = LividRGB.OFF
			Grid_44 = LividRGB.OFF
			Grid_45 = LividRGB.OFF
			Grid_46 = LividRGB.OFF
			Grid_47 = LividRGB.OFF
			Grid_48 = LividRGB.OFF
			Grid_49 = LividRGB.OFF
			Grid_50 = LividRGB.OFF
			Grid_51 = LividRGB.OFF
			Grid_52 = LividRGB.OFF
			Grid_53 = LividRGB.OFF
			Grid_54 = LividRGB.OFF
			Grid_55 = LividRGB.OFF
			Grid_56 = LividRGB.OFF
			Grid_57 = LividRGB.OFF
			Grid_58 = LividRGB.OFF
			Grid_59 = LividRGB.OFF
			Grid_60 = LividRGB.OFF
			Grid_61 = LividRGB.OFF
			Grid_62 = LividRGB.OFF
			Grid_63 = LividRGB.OFF

		class Channel_12:
			Grid_0 = LividRGB.OFF
			Grid_1 = LividRGB.OFF
			Grid_2 = LividRGB.OFF
			Grid_3 = LividRGB.OFF
			Grid_4 = LividRGB.OFF
			Grid_5 = LividRGB.OFF
			Grid_6 = LividRGB.OFF
			Grid_7 = LividRGB.OFF
			Grid_8 = LividRGB.OFF
			Grid_9 = LividRGB.OFF
			Grid_10 = LividRGB.OFF
			Grid_11 = LividRGB.OFF
			Grid_12 = LividRGB.OFF
			Grid_13 = LividRGB.OFF
			Grid_14 = LividRGB.OFF
			Grid_15 = LividRGB.OFF
			Grid_16 = LividRGB.OFF
			Grid_17 = LividRGB.OFF
			Grid_18 = LividRGB.OFF
			Grid_19 = LividRGB.OFF
			Grid_20 = LividRGB.OFF
			Grid_21 = LividRGB.OFF
			Grid_22 = LividRGB.OFF
			Grid_23 = LividRGB.OFF
			Grid_24 = LividRGB.OFF
			Grid_25 = LividRGB.OFF
			Grid_26 = LividRGB.OFF
			Grid_27 = LividRGB.OFF
			Grid_28 = LividRGB.OFF
			Grid_29 = LividRGB.OFF
			Grid_30 = LividRGB.OFF
			Grid_31 = LividRGB.OFF
			Grid_32 = LividRGB.OFF
			Grid_33 = LividRGB.OFF
			Grid_34 = LividRGB.OFF
			Grid_35 = LividRGB.OFF
			Grid_36 = LividRGB.OFF
			Grid_37 = LividRGB.OFF
			Grid_38 = LividRGB.OFF
			Grid_39 = LividRGB.OFF
			Grid_40 = LividRGB.OFF
			Grid_41 = LividRGB.OFF
			Grid_42 = LividRGB.OFF
			Grid_43 = LividRGB.OFF
			Grid_44 = LividRGB.OFF
			Grid_45 = LividRGB.OFF
			Grid_46 = LividRGB.OFF
			Grid_47 = LividRGB.OFF
			Grid_48 = LividRGB.OFF
			Grid_49 = LividRGB.OFF
			Grid_50 = LividRGB.OFF
			Grid_51 = LividRGB.OFF
			Grid_52 = LividRGB.OFF
			Grid_53 = LividRGB.OFF
			Grid_54 = LividRGB.OFF
			Grid_55 = LividRGB.OFF
			Grid_56 = LividRGB.OFF
			Grid_57 = LividRGB.OFF
			Grid_58 = LividRGB.OFF
			Grid_59 = LividRGB.OFF
			Grid_60 = LividRGB.OFF
			Grid_61 = LividRGB.OFF
			Grid_62 = LividRGB.OFF
			Grid_63 = LividRGB.OFF

		class Channel_13:
			Grid_0 = LividRGB.OFF
			Grid_1 = LividRGB.OFF
			Grid_2 = LividRGB.OFF
			Grid_3 = LividRGB.OFF
			Grid_4 = LividRGB.OFF
			Grid_5 = LividRGB.OFF
			Grid_6 = LividRGB.OFF
			Grid_7 = LividRGB.OFF
			Grid_8 = LividRGB.OFF
			Grid_9 = LividRGB.OFF
			Grid_10 = LividRGB.OFF
			Grid_11 = LividRGB.OFF
			Grid_12 = LividRGB.OFF
			Grid_13 = LividRGB.OFF
			Grid_14 = LividRGB.OFF
			Grid_15 = LividRGB.OFF
			Grid_16 = LividRGB.OFF
			Grid_17 = LividRGB.OFF
			Grid_18 = LividRGB.OFF
			Grid_19 = LividRGB.OFF
			Grid_20 = LividRGB.OFF
			Grid_21 = LividRGB.OFF
			Grid_22 = LividRGB.OFF
			Grid_23 = LividRGB.OFF
			Grid_24 = LividRGB.OFF
			Grid_25 = LividRGB.OFF
			Grid_26 = LividRGB.OFF
			Grid_27 = LividRGB.OFF
			Grid_28 = LividRGB.OFF
			Grid_29 = LividRGB.OFF
			Grid_30 = LividRGB.OFF
			Grid_31 = LividRGB.OFF
			Grid_32 = LividRGB.OFF
			Grid_33 = LividRGB.OFF
			Grid_34 = LividRGB.OFF
			Grid_35 = LividRGB.OFF
			Grid_36 = LividRGB.OFF
			Grid_37 = LividRGB.OFF
			Grid_38 = LividRGB.OFF
			Grid_39 = LividRGB.OFF
			Grid_40 = LividRGB.OFF
			Grid_41 = LividRGB.OFF
			Grid_42 = LividRGB.OFF
			Grid_43 = LividRGB.OFF
			Grid_44 = LividRGB.OFF
			Grid_45 = LividRGB.OFF
			Grid_46 = LividRGB.OFF
			Grid_47 = LividRGB.OFF
			Grid_48 = LividRGB.OFF
			Grid_49 = LividRGB.OFF
			Grid_50 = LividRGB.OFF
			Grid_51 = LividRGB.OFF
			Grid_52 = LividRGB.OFF
			Grid_53 = LividRGB.OFF
			Grid_54 = LividRGB.OFF
			Grid_55 = LividRGB.OFF
			Grid_56 = LividRGB.OFF
			Grid_57 = LividRGB.OFF
			Grid_58 = LividRGB.OFF
			Grid_59 = LividRGB.OFF
			Grid_60 = LividRGB.OFF
			Grid_61 = LividRGB.OFF
			Grid_62 = LividRGB.OFF
			Grid_63 = LividRGB.OFF


## a
