import os
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, Input
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from .utils import create_splits

def convert_images_to_rgb(dataset_dir):
    """Convert all images to RGB to avoid grayscale issues."""
    for split in ['train', 'val', 'test']:
        split_dir = os.path.join(dataset_dir, split)
        if not os.path.exists(split_dir):
            continue
        for cls in os.listdir(split_dir):
            cls_path = os.path.join(split_dir, cls)
            if not os.path.isdir(cls_path):
                continue
            for img_file in os.listdir(cls_path):
                if img_file.lower().endswith(('.png','.jpg','.jpeg','.bmp','.tiff')):
                    img_path = os.path.join(cls_path, img_file)
                    try:
                        img = Image.open(img_path).convert("RGB")
                        img.save(img_path)
                        print(f"Converted {img_path} to RGB")
                    except Exception as e:
                        print(f"Skipping {img_path}: {e}")

def build_mobilenet_model(input_shape=(224,224,3), num_classes=15, dropout_rate=0.4):
    """Build MobileNetV2 model with custom top layers."""
    input_tensor = Input(shape=input_shape)
    base_model = MobileNetV2(input_tensor=input_tensor, weights='imagenet', include_top=False)
    base_model.trainable = False
    
    x = GlobalAveragePooling2D()(base_model.output)
    x = Dropout(dropout_rate)(x)
    output = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=input_tensor, outputs=output)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def train_single_model(dataset_dir, save_dir, model_name, img_size=224, batch_size=32, epochs=12):
    train_dir = os.path.join(dataset_dir, 'train')
    val_dir = os.path.join(dataset_dir, 'val')
    
    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        raise FileNotFoundError(f"Train/Val folders not found for {dataset_dir}.")

    os.makedirs(save_dir, exist_ok=True)
    
    print(f"Converting images to RGB for {model_name}...")
    convert_images_to_rgb(dataset_dir)
    print("RGB conversion completed.")

    tf.keras.backend.clear_session()

    # ---------------- Generators ----------------
    train_gen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        brightness_range=[0.8,1.2]
    ).flow_from_directory(train_dir, target_size=(img_size,img_size), batch_size=batch_size, class_mode='categorical', color_mode='rgb')

    val_gen = ImageDataGenerator(rescale=1./255).flow_from_directory(val_dir, target_size=(img_size,img_size), batch_size=batch_size, class_mode='categorical', color_mode='rgb')

    print(f"Found {train_gen.samples} training images and {val_gen.samples} validation images")
    print(f"Number of classes: {train_gen.num_classes}")
    print(f"Class indices: {train_gen.class_indices}")

    # ---------------- Model ----------------
    model = build_mobilenet_model(input_shape=(img_size,img_size,3), num_classes=train_gen.num_classes)

    # ---------------- Callbacks ----------------
    model_path = os.path.join(save_dir, 'best_model.h5')
    callbacks = [
        ModelCheckpoint(model_path, monitor='val_accuracy', save_best_only=True, verbose=1, mode='max'),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-7, verbose=1),
        EarlyStopping(monitor='val_accuracy', patience=7, restore_best_weights=True, verbose=1, mode='max')
    ]

    print("Starting training...")
    model.fit(train_gen, validation_data=val_gen, epochs=epochs, callbacks=callbacks, verbose=1)

    print(f"[{model_name}] Training completed. Model saved at {model_path}")
    
    # Save class indices
    class_indices_path = os.path.join(save_dir, 'class_indices.txt')
    with open(class_indices_path,'w') as f:
        for class_name,index in train_gen.class_indices.items():
            f.write(f"{class_name}: {index}\n")

    return model, train_gen.class_indices

# ------------------ RUN ALL MODELS ------------------
if __name__ == "__main__":
    datasets_root = "../datasets"
    data_root = "../data"
    models_root = "../models"

    os.makedirs(data_root, exist_ok=True)
    os.makedirs(models_root, exist_ok=True)

    model_names = [d for d in os.listdir(datasets_root) if os.path.isdir(os.path.join(datasets_root,d))]
    if not model_names:
        print(f"No dataset directories found in {datasets_root}")
        exit(1)

    for model_name in model_names:
        print(f"\nProcessing dataset: {model_name}")
        src_dataset = os.path.join(datasets_root, model_name)
        dest_dataset = os.path.join(data_root, model_name)
        save_dir = os.path.join(models_root, model_name)
        os.makedirs(save_dir, exist_ok=True)

        try:
            create_splits(src_dataset, dest_dataset)
            train_single_model(dest_dataset, save_dir, model_name)
        except Exception as e:
            print(f"Skipping {model_name} due to error: {e}")
            continue

    print("All datasets processed!")
