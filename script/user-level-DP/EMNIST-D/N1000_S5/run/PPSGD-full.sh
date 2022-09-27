args=(--alg PPSGD
    #  model configuration
    --model mlp
    #  dataset configuration
    --dataset emnist_d
    --shard_per_user 5
    --num_classes 10
    #  experiment configuration
    #         --data_augmentation
    #         --data_augmentation_multiplicity 16
    --epochs 400
    --seed 1
    --num_users 1000
    #  DP configuration
    #      --disable-dp
    --dp_type user-level-DP
    --epsilon 1
    --delta 1e-5
    --dp_clip .5
    #  save/load configuration
    #  backend configuration
    --use_ray
    --ray_gpu_fraction .25
    #  test configuration
    --print_freq 2
    --print_diff_norm
    #  train configuration
    --frac_participate 1
    --batch_size 100
    --local_ep 1
    # --verbose
    # algorithm specific configuration
    --lr 1e-2
    --lr-head 1e-1
    --local_head_ep 1
    )

CUDA_VISIBLE_DEVICES=0,1,2,3 python main.py "${args[@]}"
