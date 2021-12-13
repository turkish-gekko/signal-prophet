import os
import pandas as pd
import glob
from csv import writer
from ml.model_classes.prophet_model import ProphetModel


def model_egit_tahmin_et(train, additional_feature_data):
    m_params = {
        "changepoint_prior_scale": 0.1,
        "seasonality_prior_scale": 1,
        "holidays_prior_scale": 1,
        "outlier_remove_window": 0,
    }
    model = ProphetModel(
        train=train,
        additional_features=additional_feature_data,
        changepoint_prior_scale=m_params.get("changepoint_prior_scale"),
        seasonality_prior_scale=m_params.get("seasonality_prior_scale"),
        holidays_prior_scale=m_params.get("holidays_prior_scale"),
        changepoint_range=m_params.get("changepoint_range"),
        outlier_remove_window=m_params.get("outlier_remove_window"),
        horizon=1,
    )
    model.fit()
    return model.predict()


def tahminlere_ekle(_config, tahminler):
    with open(f'./coindata/{_config.get("coin")}/tahminler.csv', 'a', newline='') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(tahminler)
        f_object.close()


def butun_dosyalari_yukle(coin, bugun, cesit):
    folder_path = f'./coindata/{coin}/daily/{cesit}/'
    tum_data_dosya_adi = f'./coindata/{coin}/{cesit}_all.csv'
    main_dataframe = None
    print(f'------butun_dosyalari_yukle {cesit}--------')
    try:
        # os.remove(tum_data_dosya_adi)
        # print('Dosya silme tamam devam et!')
        # raise('Dosya silme tamam devam et!')
        df_all = pd.read_csv(tum_data_dosya_adi)
        main_dataframe = df_all
        if bugun not in main_dataframe['Open Time'].values:
            bugunun_datasi = pd.read_csv(f'{folder_path}{coin}_{cesit}_{bugun}.csv')
            main_dataframe = pd.concat([main_dataframe, bugunun_datasi])
    except:
        # load all files
        print('dosya yuklemesi basliyor')
        file_list = glob.glob(folder_path + f"*_{cesit}_*.csv")
        main_dataframe = pd.DataFrame(pd.read_csv(file_list[0]))
        for i in range(1, len(file_list)):
            data = pd.read_csv(file_list[i])
            # df = pd.DataFrame(data)
            main_dataframe = pd.concat([main_dataframe, data])
    print('date cast basliyor')
    main_dataframe[["Open Time"]].apply(pd.to_datetime)
    main_dataframe = main_dataframe.sort_values(by='Open Time', ascending=False, ignore_index=True)
    main_dataframe = main_dataframe.interpolate(method='pad')
    print('all dosya yazma basliyor')
    main_dataframe.to_csv(tum_data_dosya_adi, index=False)
    return main_dataframe


def train_kirp_yeniden_adlandir(df, cesit):
    train = df.iloc[:, :2]
    train = train.rename(columns={"Open Time": "ds"})
    train = train.rename(columns={cesit: "y"})
    return train


def addit_kirp(df):
    return df.iloc[:, 2:]


def kaydir_birlestir(train, additional_data):
    train = train.iloc[:-1, :]
    future_add_data = additional_data.iloc[:1, :]
    additional_data = additional_data.iloc[1:, :].reset_index(drop=True)
    train = pd.concat([train, additional_data], axis=1)
    return train, future_add_data


def model_verisini_getir(coin, bugun, cesit):
    df = butun_dosyalari_yukle(coin, bugun, cesit)
    train = train_kirp_yeniden_adlandir(df, cesit)
    additional_data = addit_kirp(df)
    train, future_add_data = kaydir_birlestir(train, additional_data)
    return train, future_add_data


if __name__ == '__main__':
    bugun = '2021-12-06'
    model_verisini_getir('ETHUSDT', bugun)