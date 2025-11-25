import csv
import os
import time
from datetime import datetime
from pathlib import Path

class MetricsLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = timestamp
        self.csv_file = self.log_dir / f"session_{timestamp}.csv"
        
        self.category = None
        self.session_start = time.time()
        self.interaction_count = 0
        
        self._initialize_csv()
    
    def _initialize_csv(self):
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp',
                'Interaction_Number',
                'Target_Sentence',
                'User_Transcription',
                'Transcription_Accuracy_%',
                'Phoneme_Error_Rate_%',
                'Fluency_Score',
                'Prosody_Score',
                'Pitch_Variation_%',
                'Pause_Frequency',
                'Overall_Confidence',
                'Recording_Time_Sec',
                'Transcription_Time_Sec',
                'Analysis_Time_Sec',
                'Feedback_Generation_Time_Sec',
                'Total_Pipeline_Time_Sec',
                'Feedback'
            ])
    
    def set_category(self, category):
        self.category = category
    
    def log_interaction(self, interaction_data, timings=None):
        self.interaction_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if timings is None:
            timings = {
                'recording': 0,
                'transcription': 0,
                'analysis': 0,
                'feedback': 0,
                'total': 0
            }
        
        row = [
            timestamp,
            self.interaction_count,
            interaction_data.get('target_sentence', ''),
            interaction_data.get('user_transcription', ''),
            round(interaction_data.get('transcription_accuracy', 0), 2),
            round(interaction_data.get('phoneme_accuracy', 0), 2),
            round(interaction_data.get('fluency_score', 0), 2),
            round(interaction_data.get('prosody_score', 0), 2),
            round(interaction_data.get('pitch_variation', 0), 2),
            round(interaction_data.get('pause_frequency', 0), 3),
            round(interaction_data.get('overall_confidence', 0), 2),
            round(timings.get('recording', 0), 2),
            round(timings.get('transcription', 0), 2),
            round(timings.get('analysis', 0), 2),
            round(timings.get('feedback', 0), 2),
            round(timings.get('total', 0), 2),
            interaction_data.get('feedback', '')
        ]
        
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    
    def get_session_summary(self):
        if not os.path.exists(self.csv_file):
            return {
                'total_interactions': 0,
                'average_accuracy': 0,
                'average_phoneme_accuracy': 0,
                'total_time': 0
            }
        
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            return {
                'total_interactions': 0,
                'average_accuracy': 0,
                'average_phoneme_accuracy': 0,
                'total_time': 0
            }
        
        total_accuracy = sum(float(row['Transcription_Accuracy_%']) for row in rows)
        total_phoneme = sum(float(row['Phoneme_Error_Rate_%']) for row in rows)
        total_pipeline_time = sum(float(row['Total_Pipeline_Time_Sec']) for row in rows)
        
        num_interactions = len(rows)
        
        return {
            'total_interactions': num_interactions,
            'average_accuracy': round(total_accuracy / num_interactions, 2),
            'average_phoneme_accuracy': round(100 - (total_phoneme / num_interactions), 2),
            'total_time': round(total_pipeline_time, 2),
            'average_time_per_interaction': round(total_pipeline_time / num_interactions, 2),
            'category': self.category
        }
    
    def print_summary(self):
        summary = self.get_session_summary()
        
        print("\n" + "="*60)
        print("📊 SESSION SUMMARY")
        print("="*60)
        print(f"Category: {summary.get('category', 'Unknown')}")
        print(f"Total Interactions: {summary['total_interactions']}")
        print(f"Average Transcription Accuracy: {summary['average_accuracy']}%")
        print(f"Average Phoneme Accuracy: {summary['average_phoneme_accuracy']}%")
        print(f"Total Pipeline Time: {summary['total_time']} seconds")
        print(f"Average Time per Interaction: {summary['average_time_per_interaction']} seconds")
        print(f"\n💾 Detailed CSV log: {self.csv_file}")
        print("="*60)
