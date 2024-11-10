import tensorflow
import librosa
import joblib
import numpy as np

class Audio_Processing:
    def __init__(self):
        self.model=joblib.load("./src/pipelines/Model.pkl")
    
    def preprocess_audio(self,file_path, max_pad_len=174):
        try:
            # Load the audio file
            audio, sample_rate = librosa.load(file_path, sr=16000)
            
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=20)
            
            # Pad or truncate the MFCCs to ensure they have a consistent length
            if mfccs.shape[1] > max_pad_len:
                mfccs = mfccs[:, :max_pad_len]
            else:
                pad_width = max_pad_len - mfccs.shape[1]
                mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
            
            # Add an extra dimension to match the input shape of the model
            mfccs = mfccs.reshape(1, 20, max_pad_len, 1)
            
            return mfccs
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def process_audio(self,audio_path):
        preprocessed_audio = self.preprocess_audio(audio_path)

        # Make predictions
        if preprocessed_audio is not None:
            prediction = self.model.predict(preprocessed_audio)
            # Convert the prediction to a label
            label = 'Scream' if prediction[0] > 0.7 else 'Non-Scream'
            return label
        else:
            print("Error in preprocessing the audio file.")

if __name__=="__main__":
    audio_processing = Audio_Processing()
    audio_processing.process_audio("../test-scream.wav")
