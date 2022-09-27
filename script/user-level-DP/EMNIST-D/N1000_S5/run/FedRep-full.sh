args=(--alg DP_FedRep
    #  model configuration
    --model mlp
    #  dataset configuration
    --dataset emnist_d
    --shard_per_user 5
    --num_classes 10
    #  experiment configuration
    #         --data_augmentation
    #         --data_augmentation_multiplicity 16
    --epochs 600
    --seed 1
    --num_users 1000
    #  DP configuration
    --disable-dp
    #  save/load configuration
    #  backend configuration
    --use_ray
    --ray_gpu_fraction .33
    #  test configuration
    --print_freq 2
    --print_diff_norm
    #  train configuration
    --frac_participate .1
    --batch_size 100
    --local_ep 2
    # --verbose
    # algorithm specific configuration
    --lr 1e-2
    --lr-head 1e-2
    --local_head_ep 15
    )

CUDA_VISIBLE_DEVICES=0,1,2,3 python main.py "${args[@]}"