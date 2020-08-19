import base.pre_process as pre_process
from keras.models import Sequential
from keras.layers import LSTM, Dense, TimeDistributed, RNN, Dropout
from keras import optimizers
import base.pipline as market
import configobj
from sklearn.preprocessing import MinMaxScaler

def build_model(input_shape):
    model = Sequential()
    model.add(LSTM(32, return_sequences=True, input_shape=(None, input_shape)))
    model.add(LSTM(32, return_sequences=True, input_shape=(None, input_shape)))
    model.add(LSTM(32, return_sequences=True, input_shape=(None, input_shape)))
    model.add(Dropout(0.8))
    # model.add(LSTM(1, return_sequences=True))
    # model.add(LSTM(8, return_sequences=True))
    # # model.add(LSTM(8, return_sequences=True))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(TimeDistributed(Dense(1, activation='relu')))
    # model.add(TimeDistributed(Dense(2, activation='sigmoid')))
    print(model.summary())
    return model


if __name__ == '__main__':
    config = r"C:\Users\Administrator\PycharmProjects\TFML\cfg\LSTM.cfg"
    # data_path = r"data\csvData\scaled_data.csv"
    config = configobj.ConfigObj(config, encoding='UTF8')
    pipline = market.MLpipline(config)

    input_shape = pipline.getInputShape()

    model = build_model(input_shape=input_shape)
    # model.add(TimeDistributed(Dense(2, activation='sigmoid')))
    # model.compile(loss='categorical_crossentropy',
    #               optimizer='adam')
    sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='mean_squared_error',
                  optimizer=sgd,
                  metrics=['accuracy'])
    x_train, y_train, x_test, y_test = pipline.getTestTrainData()
    for inst in pipline.getInstCode():
        pipline.getScaledFrames(inst).to_csv(r"..\data\csvData\scaled_data_{}.csv".format(inst))
        model.fit(x_train[inst], y_train[inst], batch_size=64, validation_data=(x_test[inst], y_test[inst]),
                  steps_per_epoch=50, epochs=50)
        # model.predict()

# codes = "600276"
# P = pre_process.ProcessStrategy(
#     state_codes="600276",
#     start_date="2017-07-01",
#     end_date="2020-07-15",
#     scaler=MinMaxScaler,
#     # pre_process_strategy =
# )
# dates, scaled_frames, origin_frames, post_frames = P.process()