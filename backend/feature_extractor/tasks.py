from celery_app import app
from django.conf import settings
from urllib.parse import urljoin
from django.http import HttpRequest
from celery import shared_task
import matplotlib.pylab as plt
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import os
from tensorflow.keras.preprocessing.image import load_img, img_to_array


import logging

logger = logging.getLogger(__name__)

@shared_task
def train_model(training_session_id, *args, **kwargs):
    from .models import TFModel  
    from .models import TrainingSession
    from .models import Epoch

    if not training_session_id:
        training_session_id = args[0]
    
    session_instance = TrainingSession.objects.get(id=training_session_id)
    model_instance = TFModel.objects.get(id=session_instance.model.id)
    model_batch_size = model_instance.batch_size
    model_epochs = model_instance.epochs
    model_validation_split = model_instance.validation_split
    model_data_augmentation = model_instance.data_augmentation

    session_instance.status = 'Training'
    session_instance.save()

    try:
        
        logger.info(f"Training model {model_instance.name} with id {model_instance.id}")
        logger.info(f"Batch size: {model_batch_size}")
        logger.info(f"Epochs: {model_epochs}")
        logger.info(f"Validation split: {model_validation_split}")
        
        logger.info('Starting training...')

        print("TF version:", tf.__version__)
        print("Hub version:", hub.__version__)
        print("GPU is", "available" if tf.config.list_physical_devices('GPU') else "NOT AVAILABLE")

        #@title
        # Selection of the pre train model  
        

        model_name = model_instance.pre_model
        
        model_handle_map = {
        "efficientnetv2-s": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_s/feature_vector/2",
        "efficientnetv2-m": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_m/feature_vector/2",
        "efficientnetv2-l": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_l/feature_vector/2",
        "efficientnetv2-s-21k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_s/feature_vector/2",
        "efficientnetv2-m-21k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_m/feature_vector/2",
        "efficientnetv2-l-21k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_l/feature_vector/2",
        "efficientnetv2-xl-21k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_xl/feature_vector/2",
        "efficientnetv2-b0-21k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_b0/feature_vector/2",
        "efficientnetv2-b1-21k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_b1/feature_vector/2",
        "efficientnetv2-b2-21k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_b2/feature_vector/2",
        "efficientnetv2-b3-21k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_b3/feature_vector/2",
        "efficientnetv2-s-21k-ft1k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_s/feature_vector/2",
        "efficientnetv2-m-21k-ft1k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_m/feature_vector/2",
        "efficientnetv2-l-21k-ft1k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_l/feature_vector/2",
        "efficientnetv2-xl-21k-ft1k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_xl/feature_vector/2",
        "efficientnetv2-b0-21k-ft1k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_b0/feature_vector/2",
        "efficientnetv2-b1-21k-ft1k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_b1/feature_vector/2",
        "efficientnetv2-b2-21k-ft1k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_b2/feature_vector/2",
        "efficientnetv2-b3-21k-ft1k": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_b3/feature_vector/2",
        "efficientnetv2-b0": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_b0/feature_vector/2",
        "efficientnetv2-b1": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_b1/feature_vector/2",
        "efficientnetv2-b2": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_b2/feature_vector/2",
        "efficientnetv2-b3": "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_b3/feature_vector/2",
        "efficientnet_b0": "https://tfhub.dev/tensorflow/efficientnet/b0/feature-vector/1",
        "efficientnet_b1": "https://tfhub.dev/tensorflow/efficientnet/b1/feature-vector/1",
        "efficientnet_b2": "https://tfhub.dev/tensorflow/efficientnet/b2/feature-vector/1",
        "efficientnet_b3": "https://tfhub.dev/tensorflow/efficientnet/b3/feature-vector/1",
        "efficientnet_b4": "https://tfhub.dev/tensorflow/efficientnet/b4/feature-vector/1",
        "efficientnet_b5": "https://tfhub.dev/tensorflow/efficientnet/b5/feature-vector/1",
        "efficientnet_b6": "https://tfhub.dev/tensorflow/efficientnet/b6/feature-vector/1",
        "efficientnet_b7": "https://tfhub.dev/tensorflow/efficientnet/b7/feature-vector/1",
        "bit_s-r50x1": "https://tfhub.dev/google/bit/s-r50x1/1",
        "inception_v3": "https://tfhub.dev/google/imagenet/inception_v3/feature-vector/4",
        "inception_resnet_v2": "https://tfhub.dev/google/imagenet/inception_resnet_v2/feature-vector/4",
        "resnet_v1_50": "https://tfhub.dev/google/imagenet/resnet_v1_50/feature-vector/4",
        "resnet_v1_101": "https://tfhub.dev/google/imagenet/resnet_v1_101/feature-vector/4",
        "resnet_v1_152": "https://tfhub.dev/google/imagenet/resnet_v1_152/feature-vector/4",
        "resnet_v2_50": "https://tfhub.dev/google/imagenet/resnet_v2_50/feature-vector/4",
        "resnet_v2_101": "https://tfhub.dev/google/imagenet/resnet_v2_101/feature-vector/4",
        "resnet_v2_152": "https://tfhub.dev/google/imagenet/resnet_v2_152/feature-vector/4",
        "nasnet_large": "https://tfhub.dev/google/imagenet/nasnet_large/feature_vector/4",
        "nasnet_mobile": "https://tfhub.dev/google/imagenet/nasnet_mobile/feature_vector/4",
        "pnasnet_large": "https://tfhub.dev/google/imagenet/pnasnet_large/feature_vector/4",
        "mobilenet_v2_100_224": "https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/feature_vector/4",
        "mobilenet_v2_130_224": "https://tfhub.dev/google/imagenet/mobilenet_v2_130_224/feature_vector/4",
        "mobilenet_v2_140_224": "https://tfhub.dev/google/imagenet/mobilenet_v2_140_224/feature_vector/4",
        "mobilenet_v3_small_100_224": "https://tfhub.dev/google/imagenet/mobilenet_v3_small_100_224/feature_vector/5",
        "mobilenet_v3_small_075_224": "https://tfhub.dev/google/imagenet/mobilenet_v3_small_075_224/feature_vector/5",
        "mobilenet_v3_large_100_224": "https://tfhub.dev/google/imagenet/mobilenet_v3_large_100_224/feature_vector/5",
        "mobilenet_v3_large_075_224": "https://tfhub.dev/google/imagenet/mobilenet_v3_large_075_224/feature_vector/5",
        }

        model_image_size_map = {
        "efficientnetv2-s": 384,
        "efficientnetv2-m": 480,
        "efficientnetv2-l": 480,
        "efficientnetv2-b0": 224,
        "efficientnetv2-b1": 240,
        "efficientnetv2-b2": 260,
        "efficientnetv2-b3": 300,
        "efficientnetv2-s-21k": 384,
        "efficientnetv2-m-21k": 480,
        "efficientnetv2-l-21k": 480,
        "efficientnetv2-xl-21k": 512,
        "efficientnetv2-b0-21k": 224,
        "efficientnetv2-b1-21k": 240,
        "efficientnetv2-b2-21k": 260,
        "efficientnetv2-b3-21k": 300,
        "efficientnetv2-s-21k-ft1k": 384,
        "efficientnetv2-m-21k-ft1k": 480,
        "efficientnetv2-l-21k-ft1k": 480,
        "efficientnetv2-xl-21k-ft1k": 512,
        "efficientnetv2-b0-21k-ft1k": 224,
        "efficientnetv2-b1-21k-ft1k": 240,
        "efficientnetv2-b2-21k-ft1k": 260,
        "efficientnetv2-b3-21k-ft1k": 300, 
        "efficientnet_b0": 224,
        "efficientnet_b1": 240,
        "efficientnet_b2": 260,
        "efficientnet_b3": 300,
        "efficientnet_b4": 380,
        "efficientnet_b5": 456,
        "efficientnet_b6": 528,
        "efficientnet_b7": 600,
        "inception_v3": 299,
        "inception_resnet_v2": 299,
        "nasnet_large": 331,
        "pnasnet_large": 331,
        }

        model_handle = model_handle_map.get(model_name)
        pixels = model_image_size_map.get(model_name, 224)

        print(f"Selected model: {model_name} : {model_handle}")

        IMAGE_SIZE = (pixels, pixels)
        print(f"Input size {IMAGE_SIZE}")

        BATCH_SIZE = model_batch_size 
        logger.info(f"Batch size: {BATCH_SIZE}")

        # Import dataset
        file_name = session_instance.dataset.name.replace(' ', '_').lower()
        logger.info(f"Dataset NAME: {file_name}")

        base_media_url = urljoin(settings.BASE_URL, settings.MEDIA_URL)
        logger.info(f"Dataset NAME: " + base_media_url)
        tar_path = urljoin(base_media_url, 'archive/' + file_name + '.tar.gz')    
        logger.info(f"Dataset PATH: {tar_path}")

        ## Testing Data
        # data_dir = tf.keras.utils.get_file(
        # 'flower_photos',
        # 'https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz',
        # untar=True)

        ## Testing Data
        # data_dir = tf.keras.utils.get_file(
        # 'flower_photos',
        # 'https://fossil.barberis.com/flower_photos.tar.gz',
        # untar=True)


        data_dir = tf.keras.utils.get_file(
        file_name,
        tar_path,
        untar=True)

        logger.info(f"Dataset data_dir: {data_dir}")


        ##############################################
        # Build the training and validation datasets #
        ##############################################

        logger.info("Building and compiling model...")

        def build_dataset(subset):
            return tf.keras.preprocessing.image_dataset_from_directory(
                data_dir,
                validation_split=model_validation_split,
                subset=subset,
                label_mode="categorical",
                # Seed needs to provided when using validation_split and shuffle = True.
                # A fixed seed is used so that the validation set is stable across runs.
                seed=123,
                image_size=IMAGE_SIZE,
                batch_size=1)

        train_ds = build_dataset("training")
        class_names = tuple(train_ds.class_names)
        train_size = train_ds.cardinality().numpy()
        train_ds = train_ds.unbatch().batch(BATCH_SIZE)
        train_ds = train_ds.repeat()

        normalization_layer = tf.keras.layers.Rescaling(1. / 255)
        preprocessing_model = tf.keras.Sequential([normalization_layer])
        
        do_data_augmentation = model_data_augmentation 
        if do_data_augmentation:
            preprocessing_model.add(
                tf.keras.layers.RandomRotation(40))
            preprocessing_model.add(
                tf.keras.layers.RandomTranslation(0, 0.2))
            preprocessing_model.add(
                tf.keras.layers.RandomTranslation(0.2, 0))
            # Like the old tf.keras.preprocessing.image.ImageDataGenerator(),
            # image sizes are fixed when reading, and then a random zoom is applied.
            # If all training inputs are larger than image_size, one could also use
            # RandomCrop with a batch size of 1 and rebatch later.
            preprocessing_model.add(
                tf.keras.layers.RandomZoom(0.2, 0.2))
            preprocessing_model.add(
                tf.keras.layers.RandomFlip(mode="horizontal"))
            
        @tf.function
        def preprocess(images, labels):
            return preprocessing_model(images), labels

        @tf.function
        def normalization(images, labels):
            return normalization_layer(images), labels
        
        train_ds = train_ds.map(preprocess)    

        val_ds = build_dataset("validation")
        valid_size = val_ds.cardinality().numpy()
        val_ds = val_ds.unbatch().batch(BATCH_SIZE)

        val_ds = val_ds.map(normalization) 



        ###################
        # Build the model #
        ###################

        do_fine_tuning = False #@param {type:"boolean"}

        print("Building model with", model_handle)
        model = tf.keras.Sequential([
            # Explicitly define the input shape so the model can be properly
            # loaded by the TFLiteConverter
            tf.keras.layers.InputLayer(input_shape=IMAGE_SIZE + (3,)),
            hub.KerasLayer(model_handle, trainable=do_fine_tuning),
            tf.keras.layers.Dropout(rate=0.2),
            tf.keras.layers.Dense(len(class_names),
                                kernel_regularizer=tf.keras.regularizers.l2(0.0001))
        ])
        model.build((None,)+IMAGE_SIZE+(3,))
        model.summary()



        ###################
        # Train the model #
        ###################

        logger.info("Starting model training...")

        model.compile(
            optimizer=tf.keras.optimizers.SGD(learning_rate=0.005, momentum=0.9), 
            loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True, label_smoothing=0.1),
            metrics=['accuracy'])

        steps_per_epoch = train_size // BATCH_SIZE
        validation_steps = valid_size // BATCH_SIZE
        # Fit the model and get the History object
        history_obj = model.fit(
            train_ds,
            epochs=model_epochs, 
            steps_per_epoch=steps_per_epoch,
            validation_data=val_ds,
            validation_steps=validation_steps)

        # The history attribute of the History object is a dictionary
        hist = history_obj.history 
        logger.info("Training completed")

        # Now, you can log the contents of the hist dictionary
        for epoch in range(1, len(hist['accuracy']) + 1):
            accuracy = hist['accuracy'][epoch - 1]
            loss = hist['loss'][epoch - 1]
            val_accuracy = hist['val_accuracy'][epoch - 1]
            val_loss = hist['val_loss'][epoch - 1]
            logger.info(f'Epoch {epoch}: Accuracy: {accuracy}, Loss: {loss}, Val Accuracy: {val_accuracy}, Val Loss: {val_loss}')



        ###################
        # Plots (object)  #
        ###################
            
        plt.figure()
        plt.ylabel("Loss (training and validation)")
        plt.xlabel("Training Steps")
        plt.ylim([0,2])
        plt.plot(hist["loss"])
        plt.plot(hist["val_loss"])

        plt.figure()
        plt.ylabel("Accuracy (training and validation)")
        plt.xlabel("Training Steps")
        plt.ylim([0,1])
        plt.plot(hist["accuracy"])
        plt.plot(hist["val_accuracy"])

        # Save metrics for each epoch        
        for epoch in range(1, len(hist['accuracy']) + 1):
            Epoch.objects.create(
                training_session=session_instance,
                number=epoch,
                accuracy=hist['accuracy'][epoch - 1],
                loss=hist['loss'][epoch - 1],
                val_accuracy=hist['val_accuracy'][epoch - 1],
                val_loss=hist['val_loss'][epoch - 1]
            )

        ###################
        # Save the model  #
        ###################

        # x, y = next(iter(val_ds))
        # image = x[0, :, :, :]
        # true_index = np.argmax(y[0])
        # plt.imshow(image)
        # plt.axis('off')
        # plt.show()

        # save the model
        model_file_name = session_instance.name.replace(' ', '_').lower()
        model_path = settings.MEDIA_ROOT / 'models' / f'{model_file_name}.h5'
        model.save(model_path)
        session_instance.model_path = model_path
        session_instance.status = 'Completed'

    except Exception as e:
        # If an error occurs, log it and update the status to 'Failed'
        print(f"Error during training: {e}")
        session_instance.status = 'Failed'

    session_instance.save()


# Predict the label of an image

@shared_task
def test_images(test_id, image_size=224):
    from .models import Test, TestResult
    from datasets.models import Image

    IMAGE_SIZE = (int(image_size), int(image_size))
    BATCH_SIZE = 1

    try:
        test_instance = Test.objects.get(id=test_id)
        test_instance.status = 'Testing'
        test_instance.save()

        model_file = test_instance.training_session.model_path
        logger.info(f"MODEL FILE: {model_file}")

        file_name = test_instance.dataset.name.replace(' ', '_').lower()
        logger.info(f"Testing Dataset Name: {file_name}")

        base_media_url = urljoin(settings.BASE_URL, settings.MEDIA_URL)
        logger.info(f"Testing Dataset NAME: " + base_media_url)
        tar_path = urljoin(base_media_url, 'archive/' + file_name + '.tar.gz')
        logger.info(f"Testing Dataset PATH: {tar_path}")

        data_dir = tf.keras.utils.get_file(
            file_name,
            tar_path,
            untar=True
        )

        logger.info(f"Dataset data_dir: {data_dir}")

        logger.info("Building and compiling model...")

        # Create the original dataset to extract class names and filenames
        original_dataset = tf.keras.preprocessing.image_dataset_from_directory(
            data_dir,
            label_mode="categorical",
            image_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE
        )
        class_names = original_dataset.class_names

        def build_dataset():
            dataset = original_dataset
            # Extract filenames and add them to the dataset
            filenames = [file_path for file_path in dataset.file_paths]
            filenames_ds = tf.data.Dataset.from_tensor_slices(filenames)
            dataset = tf.data.Dataset.zip((dataset, filenames_ds))

            return dataset.map(lambda data, fname: (data[0], data[1], fname))

        test_ds = build_dataset()
        normalization_layer = tf.keras.layers.Rescaling(1. / 255)

        def normalization(images, labels, filenames):
            return normalization_layer(images), labels, filenames

        test_ds = test_ds.map(normalization)

        model = tf.keras.models.load_model(model_file, custom_objects={'KerasLayer': hub.KerasLayer})
        softmax = tf.keras.layers.Softmax()

        for x, y, f in test_ds:
            image = x[0]
            true_index = np.argmax(y[0])
            logits = model.predict(np.expand_dims(image, axis=0))
            probabilities = softmax(logits).numpy()
            predicted_index = np.argmax(probabilities)
            predicted_label = class_names[predicted_index]
            true_label = class_names[true_index]
            confidence = probabilities[0][predicted_index]
            filename = os.path.basename(f.numpy().decode('utf-8'))

            print(f"Predicted probabilities: {probabilities[0]}")
            print(f"Predicted label: {predicted_label}, Confidence: {confidence:.2%}")
            print(f"True label: {true_label}")
            print(f"Filename: {filename}")

            # Find the Image object by filename
            try:
                image_obj = Image.objects.get(dataset=test_instance.dataset, image__icontains=filename)
            except Image.DoesNotExist:
                logger.error(f"Image with filename {filename} does not exist.")
                continue

            # Save test results
            TestResult.objects.create(
                test=test_instance,
                image=image_obj,
                true_label=true_label,
                prediction=predicted_label,
                confidence=float(confidence)
            )


        test_instance.status = 'Completed'
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        test_instance.status = 'Failed'
    finally:
        test_instance.save()



@shared_task
def test_images_from_db(test_id):
    from .models import Test, TestResult
    logger.info(f"Testing images for test id: {test_id}")

    try:
        test_instance = Test.objects.get(id=test_id)
        test_instance.status = 'Testing'
        test_instance.save()

        model_file = test_instance.training_session.model_path
        logger.info(f"MODEL FILE: {model_file}")

        # Load the model
        model = tf.keras.models.load_model(model_file, custom_objects={'KerasLayer': hub.KerasLayer})
        class_names = tuple(test_instance.dataset.labels.all().values_list('name', flat=True))

        for image in test_instance.dataset.images.all():
            logger.info(f"Testing image: {image.image.path}")

            img = load_img(image.image.path, target_size=(224, 224))
            img = img_to_array(img)
            img = img / 255.0
            img = np.expand_dims(img, axis=0)

            prediction_scores = model.predict(img)
            predicted_index = np.argmax(prediction_scores)
            predicted_label = class_names[predicted_index]
            confidence = prediction_scores[0][predicted_index]
            logger.info(f"Predicted scores: {np.array2string(prediction_scores)}")

            # Log prediction details
            logger.info(f"True label: {image.label.name}, Predicted label: {predicted_label}, Confidence: {confidence}")

            # Save test results
            TestResult.objects.create(
                test=test_instance,
                image=image,
                prediction=image.dataset.labels.get(name=predicted_label),
                confidence=float(confidence)
            )

        test_instance.status = 'Completed'
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        test_instance.status = 'Failed'
    finally:
        test_instance.save()
