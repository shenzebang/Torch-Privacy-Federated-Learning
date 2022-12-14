args=(  --alg DP_FedAvg_ft
        # FIXED CONFIGURATIONS
        #  model configuration
        --model cnn
        #  dataset configuration
        --dataset cifar100
        --shard_per_user 20
        --num_classes 100
        #  experiment configuration
        #      --data_augmentation
        --seed 1
        --num_users 100
        #  DP configuration
        --epsilon 1
        --delta 1e-5
        #  save/load configuration
        #  backend configuration
        --MAX_PHYSICAL_BATCH_SIZE 50
        #  test configuration
        #  train configuration
        --frac_participate 1.
        # algorithm specific configuration
        --lr-head 1e-2
        --ft-ep 15
        ## RAY[TUNE] parameters
        --gpus_per_trial .5
        # PARAMETERS TO BE TUNED
        --lr 1e-1
        --epochs 100
        --local_ep 1
        --batch_size 4000
        --dp_clip 1
     )

python tune_DP_methods.py "${args[@]}"

