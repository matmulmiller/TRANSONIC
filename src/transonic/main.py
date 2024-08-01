import pandas as pd
import os.path as path

from tqdm import tqdm
from src.transonic.scripts.E_curves import *
from src.transonic.modules.system_class import System
from src.transonic.modules.utilities import *
from src.transonic.scripts.model_eval import *


def main():

    args = parse_args()
    config = load_config(args.config)

    results_folder = create_results_folder(config['wd'])

    # Generates the E curves and E_theta curves
    generate_curves(config['wd'], config['input'], config['doe'])


    # Grabs the desired model class specified in config file
    model_name = config['model']
    model_class = get_model_class(
        f"src.transonic.models.{model_name}", 
        model_name
    )


    # Load design of experiments document
    doe = load_DOE(config['doe'])


    summary_df = pd.DataFrame(
        columns=[
            *config['parameters'],
            'RAE',
            'MAE', 
            'avg_residual', 
            'std_of_residual'], 
        index=doe.index
    )

    for id in tqdm(doe.index):

        S = System(id, config['wd'])
        S.get_system_characteristics(doe)

        model_instance = fit_model(model_class, config['model'], S, config)

        S.predicted_curves(S.C.time, model_instance.predict(S.C.time))

        metrics = generate_model_summary(S) 

        summary_df = append_model_summary(
            summary_df, 
            id, 
            metrics, 
            model_instance
        )


        visualize_fit(S, results_folder)


    # Save results to specified results folder in config file
    summary_df.to_csv(path.join(results_folder, 'eval_outputs.csv'))

    #plot_parser_dict = S.plotter().plot_parser_dict

    if config['plots']:

        for plt_idx, plot in enumerate(config['plots']):
            S.plotter().plot_parser_dict[plot](filename=config['plot_filenames'][plt_idx])
    else:
        plot_desired=input('Analysis is finished, would you like a plot? If not type "n" \n Types include: pred_vs_gt (Predicted E Curve vs. Ground Truth E-curve)\n')

        if plot_desired!='n':
            S.plotter().plot_parser_dict[plot](filename='requested_plot.png')

    return 0
    
if __name__ == '__main__':
    try:
        return_code = main()
    except OSError as e:
        print("\nNo file or directory error\n")
        return_code = 1
    print(f'Return Code: {return_code}')

