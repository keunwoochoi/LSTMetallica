'''Example script to generate text from Nietzsche's writings.

At least 20 epochs are required before the generated text
starts sounding coherent.

It is recommended to run this script on GPU, as recurrent
networks are quite computationally intensive.

If you try this script on new data, make sure your corpus
has at least ~100k characters. ~1M is better.
'''
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.datasets.data_utils import get_file
import keras
import numpy as np
import random
import sys
import os
import pdb


def sample(a, temperature=1.0):
	# helper function to sample an index from a probability array
	a = np.log(a) / temperature
	a = np.exp(a) / np.sum(np.exp(a))
	return np.argmax(np.random.multinomial(1, a, 1))

def run(is_character=False, maxlen=None, num_units=None, model_prefix=''):

	character_mode = is_character

	if character_mode:
		if maxlen == None:
			maxlen = 1024
		if num_units == None:
			num_units = 32
		step = 2*17 # step to create training data for truncated-BPTT
	else: # word mode
		if maxlen == None:
			maxlen = 128 #
		if num_units == None: 
			num_units = 512
		step = 8

	if character_mode:
		num_char_pred = maxlen*3/2
	else: 
		num_char_pred = 17*30

	num_layers = 2
	# 
	if character_mode:
		prefix = 'char'
	else:
		prefix = 'word'

	path = 'metallica_drums_text.txt' # Corpus file
	text = open(path).read()
	print('corpus length:', len(text))

	if character_mode:
		chars = set(text)
	else:
		chord_seq = text.split(' ')
		chars = set(chord_seq)
		text = chord_seq

	char_indices = dict((c, i) for i, c in enumerate(chars))
	indices_char = dict((i, c) for i, c in enumerate(chars))
	num_chars = len(char_indices)
	print('total chars:', num_chars)

	# cut the text in semi-redundant sequences of maxlen characters

	sentences = []
	next_chars = []
	for i in range(0, len(text) - maxlen, step):
		sentences.append(text[i: i + maxlen])
		next_chars.append(text[i + maxlen])
	print('nb sequences:', len(sentences))
	print('Vectorization...')
	X = np.zeros((len(sentences), maxlen, num_chars), dtype=np.bool)
	y = np.zeros((len(sentences), num_chars), dtype=np.bool)
	for i, sentence in enumerate(sentences):
		for t, char in enumerate(sentence):
			X[i, t, char_indices[char]] = 1
		y[i, char_indices[next_chars[i]]] = 1

	# build the model: 2 stacked LSTM
	print('Build model...')
	model = Sequential()
	for layer_idx in range(num_layers):
		if layer_idx == 0:
			model.add(LSTM(num_units, return_sequences=True, input_shape=(maxlen, num_chars)))
		else:
			model.add(LSTM(num_units, return_sequences=False))
		model.add(Dropout(0.2))

	model.add(Dense(num_chars))
	model.add(Activation('softmax'))

	model.compile(loss='categorical_crossentropy', optimizer='adam')

	result_directory = 'result_%s_%s_%d_%d_units/' % (prefix, model_prefix, maxlen, num_units)
	filepath_model = '%sbest_model.hdf' % result_directory
	description_model = '%s, %d layers, %d units, %d maxlen, %d steps' % (prefix, num_layers, num_units, maxlen, step)
	checker = keras.callbacks.ModelCheckpoint(filepath_model, monitor='loss', verbose=0, save_best_only=True, mode='auto')
	early_stop = keras.callbacks.EarlyStopping(monitor='loss', patience=15, verbose=0, mode='auto')

	if not os.path.exists(result_directory):
		os.mkdir(result_directory)

	# write a description file.
	with open(result_directory+description_model, 'w') as f_description:
		pass

	# train the model, output generated text after each iteration
	batch_size = 1024
	loss_history = []
	pt_x = [1,29,30,40,100,100,200,300,400]
	nb_epochs = [np.sum(pt_x[:i+1]) for i in range(len(pt_x))]

	# not random seed, but the same seed for all.
	start_index = random.randint(0, len(text) - maxlen - 1)


	for iteration, nb_epoch in zip(pt_x,nb_epochs):
		if os.path.exists('stop_asap.keunwoo'):
			os.remove('stop_asap.keunwoo')
			break

		print('-' * 50)
		print('Iteration', iteration)
		batch_size_not_decided = True
		while batch_size_not_decided:
			result = model.fit(X, y, batch_size=batch_size, nb_epoch=nb_epoch, callbacks=[checker, early_stop]) 
			loss_history = loss_history + result.history['loss']
			
			
		print 'Saving model after %d epochs...' % nb_epoch
		model.save_weights('%smodel_after_%d.hdf'%(result_directory, nb_epoch), overwrite=True)

		for diversity in [0.9, 1.0, 1.2]:
			with open(('%sresult_%s_iter_%02d_diversity_%4.2f.txt' % (result_directory, prefix, iteration, diversity)), 'w') as f_write:

				print()
				print('----- diversity:', diversity)
				f_write.write('diversity:%4.2f\n' % diversity)
				if character_mode:
					generated = ''
				else:
					generated = []
				sentence = text[start_index: start_index + maxlen]
				seed_sentence = text[start_index: start_index + maxlen]
				
				if character_mode:
					generated += sentence
				else:
					generated = generated + sentence
					
				
				print('----- Generating with seed:')
				
				if character_mode:
					print(sentence)
					sys.stdout.write(generated)
				else:
					print(' '.join(sentence))

				for i in xrange(num_char_pred):
					# if generated.endswith('_END_'):
					# 	break
					x = np.zeros((1, maxlen, num_chars))
					
					for t, char in enumerate(sentence):
						x[0, t, char_indices[char]] = 1.

					preds = model.predict(x, verbose=0)[0]
					next_index = sample(preds, diversity)
					next_char = indices_char[next_index]
					
					if character_mode:
						generated += next_char
						sentence = sentence[1:] + next_char
					else:
						generated.append(next_char)
						sentence = sentence[1:]
						sentence.append(next_char)

					if character_mode:
						sys.stdout.write(next_char)
					# else:
					# 	for ch in next_char:
					# 		sys.stdout.write(ch)	

					sys.stdout.flush()

				if character_mode:
					f_write.write(seed_sentence + '\n')
					f_write.write(generated)
				else:
					f_write.write(' '.join(seed_sentence) + '\n')
					f_write.write(' ' .join(generated))
		
		np.save('%sloss_%s.npy'%(result_directory, prefix), loss_history)

	print 'Done! You might want to run main_post_process.py to get midi files. '
	print 'You need python-midi (https://github.com/vishnubob/python-midi) to run it.'

if __name__=='__main__':

	for maxlen in [256]: # for wrod, 256 is about 32 bars. 
		for num_units in [128,512]:
			run(is_character=False, maxlen=maxlen, num_units=num_units)
	
