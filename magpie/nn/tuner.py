from __future__ import print_function

from hyperopt import Trials, STATUS_OK, tpe
from hyperas import optim
from hyperas.distributions import choice, uniform


def keras_data():
    from magpie.config import HEP_TEST_PATH, HEP_TRAIN_PATH
    from magpie.nn.input_data import get_data_for_model
    import fileinput

    train_generator, (x_test, y_test) = get_data_for_model(
        fileinput,  # yes, it's a hack
        as_generator=True,
        batch_size=64,
        train_dir=HEP_TRAIN_PATH,
        test_dir=HEP_TEST_PATH,
    )


def keras_model():
    import os

    from keras.models import Sequential
    from keras.layers.core import Dense
    from keras.layers.core import Dropout
    from keras.layers.normalization import BatchNormalization
    from keras.layers.recurrent import GRU

    from magpie.config import HEP_TRAIN_PATH, CONSIDERED_KEYWORDS
    from magpie.feature_extraction import EMBEDDING_SIZE
    from magpie.nn.config import SAMPLE_LENGTH

    NB_EPOCHS = 20

    model = Sequential()
    model.add(GRU(
        {{choice([512, 1024])}},
        input_dim=EMBEDDING_SIZE,
        input_length=SAMPLE_LENGTH,
        init='glorot_uniform',
        inner_init='normal',
    ))
    model.add(BatchNormalization())
    model.add(Dropout({{uniform(0.0, 0.3)}}))

    # We add a vanilla hidden layer:
    model.add(Dense({{choice([512, 1024])}}, activation='relu'))
    
    model.add(BatchNormalization())
    model.add(Dropout({{uniform(0.0, 0.3)}}))

    model.add(Dense(CONSIDERED_KEYWORDS, activation='sigmoid'))

    model.compile(
        loss='binary_crossentropy',
        optimizer='adam',
        class_mode='binary',
    )
    print('Model YAML:')
    print(model.to_yaml())

    model.fit_generator(
        train_generator,
        len({filename[:-4] for filename in os.listdir(HEP_TRAIN_PATH)}),
        NB_EPOCHS,
        verbose=2,
    )

    score = model.evaluate(x_test, y_test)
    return {'loss': score, 'status': STATUS_OK}

if __name__ == '__main__':
    best_run = optim.minimize(model=keras_model,
                              data=keras_data,
                              algo=tpe.suggest,
                              max_evals=10,
                              trials=Trials())
    print(best_run)
