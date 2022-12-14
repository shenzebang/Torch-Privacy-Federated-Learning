args=(  --alg DP_FedRep
        #  model configuration
        --model cnn
        #  dataset configuration
        --dataset cifar10
        --shard_per_user 2
        --num_classes 10
        #  experiment configuration
        #      --data_augmentation
        --epochs 500
        --seed 1
        --num_users 100
        #  DP configuration
        #      --disable-dp
        --epsilon 1
        --delta 1e-5
        --dp_clip 1
        #  save/load configuration
        #  backend configuration
        --use_ray
        --ray_gpu_fraction 0.3
        #  test configuration
        --print_freq 2
        #  train configuration
        --batch_size 4000
        --MAX_PHYSICAL_BATCH_SIZE 100
        --local_ep 1
        # --verbose
        # algorithm specific configuration
        --lr-rep 1e-1
        --lr-head 1e-2
        --local_head_ep 15
        )

CUDA_VISIBLE_DEVICES=0 python tune_DP_methods.py "${args[@]}"
