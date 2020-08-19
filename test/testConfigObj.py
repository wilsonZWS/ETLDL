import unittest
import configobj
import base.pre_process as pre_process
import base.pipline as market
from sklearn.preprocessing import MinMaxScaler
from feed import mysqlFeed

from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
import numpy as np
import os
import pandas as pd

import time

class configObjTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg = r"C:\Users\Administrator\PycharmProjects\TFML\cfg\LSTM.cfg"
        self.config = configobj.ConfigObj(self.cfg, encoding='UTF8')
        self.label = self.config['Analyze']['label']
        self.inst_list = ['IF']

    def testConfigObj(self):
        cfg = r"C:\Users\wilson.zhang\PycharmProjects\TFML\cfg\LSTM.cfg"
        config = configobj.ConfigObj(cfg, encoding='UTF8')
        label = config['Analyze']['label']
        # print (config)
        print (label)


    def testPreprocess(self):
        P = pre_process.ProcessStrategy(cfg=self.config)
        dates, scaled_frames, origin_frames, post_frames = P.process()
        for inst in self.inst_list:
            post_frames[inst].to_csv("../data/csvData/{}_post.csv".format(inst))
            scaled_frames[inst].to_csv("../data/csvData/{}_scaled.csv".format(inst))

    def testPipline(self):
        pipline = market.MLpipline(self.config)
        print ('here')


    def testbatch(self):
        scaled_frames = pd.read_csv("../data/csvData/IF_scaled.csv")
        target = scaled_frames.pop(self.label)
        scaled_frames.pop('date')
        dataset = tf.data.Dataset.from_tensor_slices((scaled_frames.values, target.values))
        for feat, targ in dataset.take(1):
            print('Features: {}, Target: {}'.format(feat, targ))

        print ("______________________")
        batchset = dataset.batch(5)
        for feat, targ in batchset.take(1):
            print('Features: {}, Target: {}'.format(feat, targ))



    def testReadCSV(self):
        PATH = R"C:\Users\Administrator\PycharmProjects\TFML\data\csvData\instList.csv"
        df = pd.read_csv(PATH)
        for inst in df['instCode']:
            print (inst)


    def testMysqlFeed(self):
        cfg = r"C:\Users\wilson.zhang\PycharmProjects\TFML\cfg\LSTM.cfg"
        config = configobj.ConfigObj(cfg, encoding='UTF8')
        # feedSrcFile = config['barfeedSrcFile']
        root_path = config['General']['rootPath'] + '\cfg\\'
        db = mysqlFeed.DBService(path=root_path, dbFile='DB-125')
        df = db.readOHLCpd(inst='IF.CFE', table='dailydata', startdate='2020-01-01', enddate='2020-07-15',
                           frame=15, DSource='DS00001')
        # barFeed = dbbarfeed.DBBarFeed(config, frame, barfeedFile=feedSrcFile)
        print (df.head(5))

    def testScales(self):
        from sklearn.preprocessing import StandardScaler
        data = [[0, 0], [0, 0], [1, 1], [1, 1]]
        self.scaler = StandardScaler()
        self.scaler.fit(data)
        print(self.scaler.mean_)
        print(self.scaler.transform(data))
        print(self.scaler.transform([[2, 2]]))

    def testNativeLSTM(self):
        def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
            model = tf.keras.Sequential([
                tf.keras.layers.Embedding(vocab_size, embedding_dim,
                                          batch_input_shape=[batch_size, None]),
                tf.keras.layers.GRU(rnn_units,
                                    return_sequences=True,
                                    stateful=True,
                                    recurrent_initializer='glorot_uniform'),
                tf.keras.layers.Dense(vocab_size)
            ])
            return model

        model = build_model(
          vocab_size=len(vocab),
          embedding_dim=embedding_dim,
          rnn_units=128,
          batch_size=64)


    def testRNN(self):
        path_to_file = tf.keras.utils.get_file('shakespeare.txt',
                                               'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')
        text = open(path_to_file, 'rb').read().decode(encoding='utf-8')
        print(text[:250])
        vocab = sorted(set(text))
        print('{} unique characters'.format(len(vocab)))
        char2idx = {u: i for i, u in enumerate(vocab)}
        idx2char = np.array(vocab)

        ### convert text to int index in the dictionary
        text_as_int = np.array([char2idx[c] for c in text])
        print('{')
        for char, _ in zip(char2idx, range(20)):
            print('  {:4s}: {:3d},'.format(repr(char), char2idx[char]))
        print('  ...\n}')
        print('{} ---- characters mapped to int ---- > {}'.format(repr(text[:13]), text_as_int[:13]))
        seq_length = 100
        examples_per_epoch = len(text) // (seq_length + 1)
        char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)
        sequences = char_dataset.batch(seq_length + 1, drop_remainder=True)
        for i in char_dataset.take(5):
            print(idx2char[i.numpy()])

        def split_input_target(chunk):
            input_text = chunk[:-1]
            target_text = chunk[1:]
            return input_text, target_text

        dataset = sequences.map(split_input_target)

        # print(list(dataset.as_numpy_iterator()))
        for input_example, target_example in dataset.take(1):
            print('Input data: ', repr(''.join(idx2char[input_example.numpy()])))
            print('Target data:', repr(''.join(idx2char[target_example.numpy()])))

            for i, (input_idx, target_idx) in enumerate(zip(input_example[:5], target_example[:5])):
                print("Step {:4d}".format(i))
                print("  input: {} ({:s})".format(input_idx, repr(idx2char[input_idx])))
                print("  expected output: {} ({:s})".format(target_idx, repr(idx2char[target_idx])))

        BATCH_SIZE = 64

        # Buffer size to shuffle the dataset
        # (TF data is designed to work with possibly infinite sequences,
        # so it doesn't attempt to shuffle the entire sequence in memory. Instead,
        # it maintains a buffer in which it shuffles elements).
        BUFFER_SIZE = 10000
        ### shuffle: prevent overfitting, change one record of train test set
        dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)
        for input_example, target_example in dataset.take(1):
            print ('here')
            # print('Input data: ', repr(''.join(idx2char[input_example.numpy()])))
            # print('Target data:', repr(''.join(idx2char[target_example.numpy()])))
        # Length of the vocabulary in chars
        vocab_size = len(vocab)
        # The embedding dimension
        embedding_dim = 256
        # Number of RNN units
        rnn_units = 1024

        def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
            model = tf.keras.Sequential([
                tf.keras.layers.Embedding(vocab_size, embedding_dim,
                                          batch_input_shape=[batch_size, None]),
                tf.keras.layers.GRU(rnn_units,
                                    return_sequences=True,
                                    stateful=True,
                                    recurrent_initializer='glorot_uniform'),
                tf.keras.layers.Dense(vocab_size)
            ])
            return model

        model = build_model(
            vocab_size=len(vocab),
            embedding_dim=embedding_dim,
            rnn_units=rnn_units,
            batch_size=BATCH_SIZE)

        def loss(labels, logits):
            return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

        for input_example_batch, target_example_batch in dataset.take(1):
            example_batch_predictions = model(input_example_batch)
            print(example_batch_predictions.shape, "# (batch_size, sequence_length, vocab_size)")
            model.summary()
            sampled_indices = tf.random.categorical(example_batch_predictions[0], num_samples=1)
            sampled_indices = tf.squeeze(sampled_indices, axis=-1).numpy()
            print (sampled_indices)
            print("Input: \n", repr("".join(idx2char[input_example_batch[0]])))
            print()
            print("Next Char Predictions: \n", repr("".join(idx2char[sampled_indices])))
            example_batch_loss = loss(target_example_batch, example_batch_predictions)
            print("Prediction shape: ", example_batch_predictions.shape, " # (batch_size, sequence_length, vocab_size)")
            print("scalar_loss:      ", example_batch_loss.numpy().mean())

        model.compile(optimizer='adam', loss=loss)

        # Directory where the checkpoints will be saved
        checkpoint_dir = '../checkpoint/training_checkpoints'
        # Name of the checkpoint files
        checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")

        checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
            filepath=checkpoint_prefix,
            save_weights_only=True)
        EPOCHS = 10
        history = model.fit(dataset, epochs=EPOCHS, callbacks=[checkpoint_callback])
        print (tf.train.latest_checkpoint(checkpoint_dir))

        model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)

        model.load_weights(tf.train.latest_checkpoint(checkpoint_dir))

        model.build(tf.TensorShape([1, None]))
        model.summary()


    def testDataSet(self):
        dataset = tf.data.Dataset.from_tensor_slices({'a': ([1, 2], [3, 4]),
                                                      'b': [5, 6]})
        print (list(dataset.as_numpy_iterator()))
        dataset = tf.data.Dataset.range(8)
        dataset = dataset.batch(3)
        print (list(dataset.as_numpy_iterator()))


    def testCache(self):
        dataset = tf.data.Dataset.range(5)
        dataset = dataset.cache("/cache/")
        print(list(dataset.as_numpy_iterator()))










