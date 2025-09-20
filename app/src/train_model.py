import os
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping

def train_model(dataset_dir, save_dir, model_name, img_size=224, batch_size=32, epochs=12):
    train_dir = os.path.join(dataset_dir, 'train')
    val_dir = os.path.join(dataset_dir, 'val')
    os.makedirs(save_dir, exist_ok=True)

    # Generators
    train_gen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        brightness_range=[0.8,1.2]
    ).flow_from_directory(train_dir, target_size=(img_size,img_size), batch_size=batch_size, class_mode='categorical')

    val_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(val_dir, target_size=(img_size,img_size), batch_size=batch_size, class_mode='categorical')

    # Model
    base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(img_size,img_size,3))
    base_model.trainable = False
    x = GlobalAveragePooling2D()(base_model.output)
    x = Dropout(0.4)(x)
    output = Dense(train_gen.num_classes, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=output)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Callbacks
    model_path = os.path.join(save_dir, f'{model_name}.h5')
    checkpoint = ModelCheckpoint(model_path, monitor='val_accuracy', save_best_only=True, verbose=1)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, verbose=1)
    early_stop = EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True)

    model.fit(train_gen, validation_data=val_gen, epochs=epochs, callbacks=[checkpoint, reduce_lr, early_stop])

    # Optional fine-tuning
    base_model.trainable = True
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-5), loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(train_gen, validation_data=val_gen, epochs=5, callbacks=[checkpoint, reduce_lr, early_stop])

    print(f"Model {model_name} saved at {model_path}")
    return model, train_gen.class_indices
