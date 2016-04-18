import sys
import os
import pdb

import midi

from drum_note_processor import *


def text_to_notes(encoded_drums, note_list=None):
	''' 
	0b0000000000 0b10000000 ...  -> corresponding note. 
	'''
	if note_list == None:
		note_list = Note_List()

	for word_idx, word in enumerate(encoded_drums):
		c_tick_here = word_idx*min_ppq

		for pitch_idx, pitch in enumerate(allowed_pitch):

			if word[pitch_idx+2] == '1':
				new_note = Note(pitch, c_tick_here)
				note_list.add_note(new_note)
	return note_list


def conv_text_to_midi(filename):
	if os.path.exists(filename[:-4]+'.mid'):
		return
	f = open(filename, 'r')
	f.readline() # title
	f.readline() # seed sentence
	sentence = f.readline()
	encoded_drums = sentence.split(' ')

	#find the first BAR
	
	first_bar_idx = encoded_drums.index('BAR')
	
	encoded_drums = encoded_drums[first_bar_idx:]
	try:
		encoded_drums = [ele for ele in encoded_drums if ele not in ['BAR', 'SONG_BEGIN', 'SONG_END', '']]
	except:
		pdb.set_trace()

	# prepare output
	note_list = Note_List()
	pattern = midi.Pattern()
	track = midi.Track()
	#??
	PPQ = 220
	min_ppq = PPQ / (event_per_bar/4)
	track.resolution = PPQ # ???? too slow. why??
	# track.resolution = 192
	pattern.append(track)

	velocity = 84
	duration = min_ppq*9/10  # it is easier to set new ticks if duration is shorter than _min_ppq

	note_list = text_to_notes(encoded_drums, note_list=note_list)
	
	max_c_tick = 0 
	not_yet_offed = [] # set of midi.pitch object 
	for note_idx, note in enumerate(note_list.notes[:-1]):
		# add onset
		tick_here = note.c_tick - max_c_tick
		pitch_here = pitch_to_midipitch[note.pitch]
		# if pitch_here in cymbals_pitch: # "Lazy-off" for cymbals 
		# 	off = midi.NoteOffEvent(tick=0, pitch=pitch_here)
		# 	track.append(off)
		
		on = midi.NoteOnEvent(tick=tick_here, velocity=velocity, pitch=pitch_here)
		track.append(on)
		max_c_tick = max(max_c_tick, note.c_tick)
		# add offset for something not cymbal
		
		# if note_list.notes[note_idx+1].c_tick == note.c_tick:
		# 	if pitch_here not in cymbals_pitch:
		# 	# 	not_yet_offed.append(pitch_here)

		# else:
		# check out some note that not off-ed.
		for off_idx, waiting_pitch in enumerate(not_yet_offed):
			if off_idx == 0:
				off = midi.NoteOffEvent(tick=duration, pitch=waiting_pitch)
				max_c_tick = max_c_tick + duration
			else:
				off = midi.NoteOffEvent(tick=0, pitch=waiting_pitch)
			track.append(off)
			not_yet_offed = [] # set of midi.pitch object 

	# finalise
	if note_list.notes == []:
		print 'No notes in %s' % filename
		return
		pdb.set_trace()
	note = note_list.notes[-1]
	tick_here = note.c_tick - max_c_tick
	pitch_here = pitch_to_midipitch[note.pitch]
	on = midi.NoteOnEvent(tick=tick_here, velocity=velocity, pitch=pitch_here)
	off = midi.NoteOffEvent(tick=duration, pitch=pitch_here)

	for off_idx, waiting_pitch in enumerate(not_yet_offed):
		off = midi.NoteOffEvent(tick=0, pitch=waiting_pitch)

	# end of track event
	eot = midi.EndOfTrackEvent(tick=1)
	track.append(eot)
	# print pattern
	midi.write_midifile(filename[:-4]+'.mid', pattern)


if __name__ == '__main__':

	result_dir = sys.argv[1]
	filenames = os.listdir(result_dir) # specify which folder result_*.txt files are stored in
	filenames = [f for f in filenames if f.startswith('result') and f.endswith('.txt')]
	filenames = [f for f in filenames if os.path.getsize(result_dir + '/' + f) != 0]
	for filename in filenames:
		conv_text_to_midi(result_dir + '/' + filename)

	print 'Texts -> midi done! for %d files' % len(filenames)

