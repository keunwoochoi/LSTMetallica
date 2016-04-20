#LSTMetallica

A LSTM network that learns from the drum tracks of Metallica and generates new tracks.

#### Prequisite
 * [keras](https://github.com/fchollet/keras), a deeplearning framework
 * [python-midi](https://github.com/vishnubob/python-midi) to get midi file
 * numpy - probably you already have it.

#### Usage
 * Clond the repo
 * `$ python main_lstM_etallica.py`
 * `$ python main_post_process.py` - this is when you need [python-midi](https://github.com/vishnubob/python-midi)
 * Use [this text file](https://github.com/keunwoochoi/LSTMetallica/blob/master/metallica_drums_text.txt), an aggregated-and-encoded text file for Metallica's drum tracks, to do something more
 * [This folder](https://github.com/keunwoochoi/LSTMetallica/tree/master/Metallica_drums_midi) contains the original drum midi tracks.
 
#### External links
 * Details in my [blot post](https://keunwoochoi.wordpress.com/2016/02/23/lstmetallica/)
 * [Results on soundcloud](https://soundcloud.com/kchoi-research/sets/lstmetallica-drums) and [+1 more result](https://soundcloud.com/kchoi-research/00-24-100-bonus-for-score)
 * Similar work on jazz chord progression: [repository](https://github.com/keunwoochoi/lstm_real_book/blob/master/README.md), [blog post](https://keunwoochoi.wordpress.com/2016/02/19/lstm-realbook/), [soundcloud](https://soundcloud.com/kchoi-research/sets/lstm-realbook-1-5)

### Citation
**Text-based LSTM networks for Automatic Music Composition**, Keunwoo Choi, George Fazekas, Mark Sandler, *1st Conference on Computer Simulation of Musical Creativity*, Huddersfield, UK, 2016, [arXiv](https://arxiv.org/abs/1604.05358#), [pdf](https://arxiv.org/pdf/1604.05358v1)

