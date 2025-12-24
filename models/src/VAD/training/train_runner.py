from .VADPipeline import VADPipeline

def main():
    pipeline = VADPipeline()
    pipeline.run_pipeline(collect_data=True, preprocess_data=True, split_data=True, train=True, evaluate=True, save_model=True)
    
    print("Finished training model")

if __name__ == '__main__':
    main()