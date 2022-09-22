args=(--alg DP_FedAvg_ft
    #  model configuration
    --model cnn
    #  dataset configuration
    --dataset cifar100
    --shard_per_user 5
    --num_classes 100
    #  experiment configuration
    #         --data_augmentation
    #         --data_augmentation_multiplicity 16
    --epochs 400
    --seed 1
    --num_users 500
    #  DP configuration
    #      --disable-dp
    --dp_type user-level-DP
    --epsilon 1
    --delta 1e-5
    --dp_clip .01
    #  save/load configuration
    #  backend configuration
#     --gpu 0-1-2-3
#     --use_ray
#     --ray_gpu_fraction .3
    #  test configuration
    #  train configuration
    --frac_participate 1
    --batch_size 100
    --local_ep 1
    # --verbose
    # algorithm specific configuration
    --lr 1e-1
    --lr-head 1e-2
    --ft-ep 15
    )

CUDA_VISIBLE_DEVICES=0,1,2,3 python main.py "${args[@]}"