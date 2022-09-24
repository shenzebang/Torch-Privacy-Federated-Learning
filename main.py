import warnings

from torchsummary import summary

from utils.common_utils import *
from utils.data_utils import prepare_dataloaders
from methods.DP_FedAvg_ft import ServerDPFedAvgFT, ClientDPFedAvgFT
from methods.DP_FedRep import ServerDPFedRep, ClientDPFedRep
from methods.PPSGD import ServerPPSGD, ClientPPSGD
from methods.DP_local_train import ServerLocalOnly, ClientLocalOnly
from methods.PMTL import ServerPMTL, ClientPMTL
from models.models import get_model
from options import args_parser
from utils.ray_remote_worker import *
from utils.plot_utils import plot_stats_in_logger
from ray import tune


ALGORITHMS = {
    "DP_FedAvg_ft"  : (ServerDPFedAvgFT, ClientDPFedAvgFT),
    "DP_FedRep"     : (ServerDPFedRep, ClientDPFedRep),
    "PPSGD"         : (ServerPPSGD, ClientPPSGD),
    "Local"         : (ServerLocalOnly, ClientLocalOnly),
    "PMTL"          : (ServerPMTL, ClientPMTL),
}



# warnings.filterwarnings("ignore")

def main(args, is_ray_tune = False, checkpoint_dir=None):
    '''
         "checkpoint_dir" will be used to ensure future compatibility with other ray.tune schedulers.
    '''
    if args.seed != 0:
        seed_all(args.seed)
        if args.verbose:
            print(
                f"[ Seed is set to {args.seed} to ensure reproducibility. ]"
            )
    else:
        if args.verbose:
            print(
                f"[ No seed is manually set. ]"
            )

    if not args.disable_dp:
        if args.dp_type == 'user-level-DP':
            print(
                "[ Ensuring user-level DP! ]"
            )
        else:
            print(
                "[ Ensuring local-level DP! ]"
            )

    device = torch.device(f'cuda' if torch.cuda.is_available() else 'cpu')


    # Determine the algorithm
    print(
        f"[ Running Algorithm {args.alg}. ]"
    )
    (Server, Client) = ALGORITHMS[args.alg]

    # Init Dataloaders
    train_dataloaders, validation_dataloaders, test_dataloaders = prepare_dataloaders(args)


    # Init model
    # If use ray, leave the models on 'cpu' to save cuda memory
    global_model = get_model(args) if args.use_ray else get_model(args).to(device)
    if "cifar" in args.dataset:
        summary(global_model, input_size=(3, 32, 32), device='cpu')
    elif "mnist" in args.dataset:
        summary(global_model, input_size=(1, 28, 28), device='cpu')

    restore_from_checkpoint(args, global_model, checkpoint_dir)


    # Init representation keys
    global_keys, local_keys, fine_tune_keys = get_keys(args, global_model)
    print(
        f"[ The global_keys keys are : ]",
        f"{global_keys}"
    )
    print(
        f"[ The local_keys keys are : ]",
        f"{local_keys}"
    )
    print(
        f"[ The fine-tine keys are : ]",
        f"{fine_tune_keys}"
    )

    # Init logger
    logger = Logger()

    # Init Clients
    clients = [Client(idx, args, global_keys, local_keys, fine_tune_keys, traindlr, testdlr, validdlr, global_model, device)
               for idx, (traindlr, validdlr, testdlr) in
               enumerate(zip(train_dataloaders, validation_dataloaders, test_dataloaders))]

    # Init Server
    remote_workers = create_remote_workers(args, device) # create remote workers with ray backend

    server = Server(args, global_model, global_keys, local_keys, fine_tune_keys, clients, remote_workers, logger, device)



    train_losses = []
    train_accs = []
    validation_losses = []
    validation_accs = []
    test_losses = []
    test_accs = []
    # Run experiment
    for epoch in range(args.epochs):
        train_loss, train_acc, validation_loss, validation_acc, test_loss, test_acc = server.step(epoch)
        if is_ray_tune:
            with tune.checkpoint_dir(step=epoch) as checkpoint_dir:
                path = os.path.join(checkpoint_dir, "checkpoint")
                torch.save(server.model.state_dict(), path)

            tune.report(
                train_loss  = train_loss.item(),
                train_acc   = train_acc.item(),
                validation_loss = validation_loss.item(),
                validation_acc = validation_acc.item(),
                test_loss   = test_loss.item(),
                test_acc    = test_acc.item()
            )

        train_losses.append(train_loss.item())
        train_accs.append(train_acc.item())
        validation_losses.append(validation_loss.item())
        validation_accs.append(validation_acc.item())
        test_losses.append(test_loss.item())
        test_accs.append(test_acc.item())

    # # Test the final model
    # # 1. Disable the partial participation
    # server.args.frac_participate = 1.
    # # 2. Call server.step(-1) to obtain train/test results WITHOUT update the model
    # train_loss, train_acc, validation_loss, validation_acc, test_loss, test_acc = server.step(-1)
    # # 3. Print the results
    # print(
    #     f"[ Final Model Performance ] After {args.epochs} global epochs, on dataset {args.dataset}, {args.alg} achieves\t"
    #     f"Validation Loss: {validation_loss:.2f} Validation Acc@1: {validation_acc * 100:.2f} \t"
    #     f"Test loss: {test_loss:.2f} Test acc@1: {test_acc * 100:.2f} "
    # )

    # Report the model with the best validation accuracy
    index = validation_accs.index(max(validation_accs))
    print(
        f"[ Performance of Model with the Best Validation Accuracy ] At {index} global epochs, on dataset {args.dataset}, {args.alg} achieves\t"
        f"Validation Loss: {validation_losses[index]:.2f} Validation Acc@1: {validation_accs[index] * 100:.2f} \t"
        f"Test loss: {test_losses[index]:.2f} Test acc@1: {test_accs[index] * 100:.2f} "
    )

    plot_directory = f"./plot/fairness_gap"
    os.makedirs(plot_directory, exist_ok=True)
    plot_stats_in_logger(logger, index, plot_directory)

    # return results
    return train_losses, train_accs, validation_losses, validation_accs, test_losses, test_accs, server.model.state_dict()




if __name__ == '__main__':
    args = args_parser()
    # args.disable_dp = True
    n_gpus = set_cuda(args)

    check_args(args)

    if args.use_ray and n_gpus > 0:
        ray.init(num_gpus=n_gpus, log_to_driver=False)
    '''
    ####################################################################################################################
        If this is the main file, call <main> with "args" as it is and "is_ray_tune" is set to False.
    ####################################################################################################################    

    ####################################################################################################################
        If using ray.tune for hyper parameter tuning, <main> will be wrapped to produce <main_tune> and "is_ray_tune" is
        set to True.

            In <main_tune>, the first input is "config", which contains the hyper parameters to be tuned by ray.tune.
                1.  According to the "config" variable, the corresponding argument in "args" will be changed.
                2.  The procedure <main> will then be called with the altered "args".
                3.  The outputs (loss, accuracy) of <main> will be returned using ray.tune.report.
    ####################################################################################################################            
    '''
    train_losses, train_accs, validation_losses, validation_accs, test_losses, test_accs, model_state = main(args)

    # '''
    # ####################################################################################################################
    #     If this is the main file, call <test_configuration> to test the trained model with "args" as it is.
    # ####################################################################################################################
    #
    #
    # ####################################################################################################################
    #     If using ray.tune for hyper parameter tuning, <test_configuration> will be wrapped to produce <test_best_model>.
    #
    #         In <test_best_model>, the input is "best_trial", which contains information about the best hyper parameters
    #         returned by ray.tune.
    #             1.  According to the "best_trial.checkpoint.value", the "model_state" will be loaded; "args" will be
    #                 altered according to the "best_trial.config".
    #             2.  The procedure <test_configuration> will be called, with the altered "args" and the loaded
    #                 "model_state".
    # ####################################################################################################################
    # '''
    # test_configuration(args, model_state)