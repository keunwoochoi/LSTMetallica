import midi
import pdb

PPQ = 480 # Pulse per quater note
event_per_bar = 16 # to quantise.
min_ppq = PPQ / (event_per_bar/4)
# ignore: 39 hand clap, 54 tambourine, 56 Cowbell, 58 Vibraslap, 60-81
drum_conversion = {35:36, # acoustic bass drum -> bass drum (36)
					37:38, 40:38, # 37:side stick, 38: acou snare, 40: electric snare
					43:41, # 41 low floor tom, 43 ghigh floor tom
					47:45, # 45 low tom, 47 low-mid tom
					50:48, # 50 high tom, 48 hi mid tom
					44:42, # 42 closed HH, 44 pedal HH
					57:49, # 57 Crash 2, 49 Crash 1
					59:51, 53:51, 55:51, # 59 Ride 2, 51 Ride 1, 53 Ride bell, 55 Splash
					52:49 # 52: China cymbal
					}
				# k, sn,cHH,oHH,LFtom,ltm,htm,Rde,Crash
allowed_pitch = [36, 38, 42, 46, 41, 45, 48, 51, 49] # 46: open HH
cymbals_pitch = [49, 51] # crash, ride
cymbals_pitch = [] # crash, ride
# pitch_to_midipitch = {36:midi.C_2, # kick # for general MIDI Drum map
# 						38:midi.D_2, # Snare
# 						39:midi.Eb_2, # hand clap (it's alive by mistake..)
# 						41:midi.F_2, # Low floor tom
# 						42:midi.Gb_2, # Close HH
# 						45:midi.A_2, # Low tom
# 						46:midi.Bb_2, # Open HH
# 						48:midi.C_3,  # Hi Mid Tom
# 						49:midi.Db_3, # Crash
# 						51:midi.Eb_3 # Ride
# 						}

pitch_to_midipitch = {36:midi.C_3,  # for logic 'SoCal' drum mapping
						38:midi.D_3, 
						39:midi.Eb_3,
						41:midi.F_3,
						42:midi.Gb_3,
						45:midi.A_3,
						46:midi.Bb_3,
						48:midi.C_4,
						49:midi.Db_4,
						51:midi.Eb_4
						}

class Note:
	def __init__(self, pitch, c_tick):
		self.pitch = pitch
		self.c_tick = c_tick # cumulated_tick of a midi note

	def add_index(self, idx):
		'''index --> 16-th note-based index starts from 0'''
		self.idx = idx

class Note_List():
	def __init__(self):
		''''''
		self.notes = []
		self.quantised = False
		self.max_idx = None

	def add_note(self, note):
		'''note: instance of Note class'''
		self.notes.append(note)

	def quantise(self, minimum_ppq):
		'''
		e.g. if minimum_ppq=120, quantise by 16-th note.
		
		'''
		if not self.quantised:
			for note in self.notes:
				note.c_tick = ((note.c_tick+minimum_ppq/2)/minimum_ppq)* minimum_ppq # quantise
				note.add_index(note.c_tick/minimum_ppq)

			self.max_idx = note.idx
			if (self.max_idx + 1) % event_per_bar != 0:
				self.max_idx += event_per_bar - ((self.max_idx + 1) % event_per_bar) # make sure it has a FULL bar at the end.
			self.quantised = True

		return

	def simplify_drums(self):
		''' use only allowed pitch - and converted not allowed pitch to the similar in a sense of drums!
		'''

		for note in self.notes:
			if note.pitch in drum_conversion: # ignore those not included in the key
				note.pitch = drum_conversion[note.pitch]
		
		self.notes = [note for note in self.notes if note.pitch in allowed_pitch]	
				
		return
	
	def return_as_text(self):
		''''''
		length = self.max_idx + 1 # of events in the track.
		event_track = []
		for note_idx in xrange(length):
			event_track.append(['0']*len(allowed_pitch))
			
		num_bars = length/event_per_bar# + ceil(len(event_texts_temp) % _event_per_bar)

		for note in self.notes:
			pitch_here = note.pitch
			note_add_pitch_index = allowed_pitch.index(pitch_here) # 0-8
			event_track[note.idx][note_add_pitch_index] = '1'
			# print note.idx, note.c_tick, note_add_pitch_index, ''.join(event_track[note.idx])
			# pdb.set_trace()
			
		event_text_temp = ['0b'+''.join(e) for e in event_track] # encoding to binary
		
		event_text = []
		# event_text.append('SONG_BEGIN')
		# event_text.append('BAR')
		for bar_idx in xrange(num_bars):
			event_from = bar_idx * event_per_bar
			event_to = event_from + event_per_bar
			event_text = event_text + event_text_temp[event_from:event_to]
			event_text.append('BAR')

		# event_text.append('SONG_END')

		return ' '.join(event_text)
		