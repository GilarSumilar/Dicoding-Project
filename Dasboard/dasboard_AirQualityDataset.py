import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import streamlit_antd_components as sac
import streamlit_shadcn_ui as ui

#Dataset
air_quality = pd.read_csv('air_quality_dataset.csv')
air_quality.rename(columns={
    'wd': 'Arah_mata_angin',
    'WSPM': 'Kecepatan_angin'
    }, inplace=True)

kadar_polutan = pd.read_csv('kadar_polutan.csv')
kadar_polutan[['SO2', 'NO2', 'CO', 'O3', 'total_kadar_polutan']] = kadar_polutan[['SO2', 'NO2', 'CO', 'O3', 'total_kadar_polutan']].apply(lambda x: x.round(2))
max_min = pd.read_csv('max_min.csv')
temp_min = -15.6

# Title
st.title("Air Quality Analysis :pencil:")


st.markdown(
    """
    ## **Dashboard**
    #### **Pertanyaan:**
    - Apakah ada korelasi antara berbagai polutan udara (PM10 & SO2, TEMP & 03, RAIN & CO)?
    - Bagaimana konsentrasi polutan udara di berbagai lokasi stasiun?
    - Apakah ada tren atau pola yang terlihat pada tingkat polutan sepanjang tahun?
    - Pada stasiun mana suhu mencapai derajat terendah dan tertingginya?
    - Pada stasiun mana curah hujan mencapai volume tertingginya? 
    
    """
    )

# Tabs
tabs = sac.tabs([
        sac.TabsItem(label='Overview', icon='house-fill'), 
        sac.TabsItem(label='Analytics', icon='bar-chart-fill'), 
        sac.TabsItem(label='Conclusion', icon='book-fill'),
], index=0, format_func='title', variant='outline', color='blue', use_container_width=True)

if tabs == 'Overview':

    column_hide = sac.checkbox(
        items=[
            'PM10',
            'SO2',
            'NO2',
            'CO',
            'O3',
            'TEMP',
            'PRES',
            'RAIN',
            'Arah_mata_angin',
            'Kecepatan_angin',
        ],
        label='Hide columns', description='Use this to hide selected columns', color='blue', index=[9,10]
    )
 
    column_mask = [col not in column_hide for col in air_quality.columns]
    filtered_air_quality = air_quality.loc[:, column_mask]

    # Ambil sampel 5 baris secara acak
    random_sample = filtered_air_quality.sample(n=50)
    # Tampilkan data secara acak
    st.dataframe(random_sample)

    col1, col2, col3 = st.columns(3)
    col1.metric("Maximum Temperature (°C)", f'{round(air_quality.TEMP.max(),1)}°C')
    col2.metric("Maximum Rain Volume (mm)", f'{round(air_quality.RAIN.max(),1)}mm')
    col3.metric("Kecepatan angin (m/s)", f'{round(air_quality.Kecepatan_angin.max(),1)}m/s')
    
    st.metric("Kadar Polutan Tertinggi", f'{round(kadar_polutan.total_kadar_polutan.max(),1)} ppm')

elif tabs == 'Analytics':
    segment = sac.segmented(
    items=[
        sac.SegmentedItem(label='Korelasi'),
        sac.SegmentedItem(label='Kadar Polutan'),
        sac.SegmentedItem(label='Tren Musiman'),
        sac.SegmentedItem(label='Temperature'),
        sac.SegmentedItem(label='Rain Volume'),
    ], description='Choose analysis from below to show', label='Analysis type', format_func='title', align='center', 
    size='sm', radius='sm', color='blue', use_container_width=True, divider=False
    )

    if segment == 'Korelasi':
        corrAQ = air_quality.corr(method= 'spearman', numeric_only=True)
        st.table(corrAQ)
        with st.expander('Penjelasan', expanded=True):
            st.markdown(
                """
                - Nilai mendekati 1: Menunjukkan korelasi positif yang kuat, artinya ketika satu variabel meningkat, variabel lainnya cenderung meningkat juga.
                - Nilai mendekati -1: Menunjukkan korelasi negatif yang kuat, artinya ketika satu variabel meningkat, variabel lainnya cenderung menurun.
                - Nilai mendekati 0: Menunjukkan tidak ada korelasi yang signifikan antara kedua variabel.
                """
            )
        with st.expander('Contoh 3 kasus:'):

            pairs = [('PM10', 'SO2'), ('TEMP', 'O3'), ('RAIN', 'CO')]

            fig, axs = plt.subplots(1, len(pairs), figsize=(12, 4))

            for i, pair in enumerate(pairs):
                x, y = pair
                axs[i].scatter(air_quality[x], air_quality[y])
                axs[i].set_xlabel(x)
                axs[i].set_ylabel(y)
                axs[i].set_title(f'Hubungan antara {x} & {y}')

                # Menambahkan garis regresi
                m, b = np.polyfit(air_quality[x], air_quality[y], 1)
                axs[i].plot(air_quality[x], m*air_quality[x] + b, color='red')

            plt.tight_layout()

            st.pyplot(fig)

            st.markdown(
                """
                **Hubungan antara PM10 & SO2**
                - Tren Positif: Terlihat adanya tren positif yang lemah antara konsentrasi PM10 dan SO2. Artinya, ketika konsentrasi PM10 meningkat, cenderung diikuti oleh peningkatan konsentrasi SO2.

                - Korelasi Moderat: Korelasi antara kedua polutan ini cenderung moderat, tidak terlalu kuat. Hal ini menunjukkan bahwa ada faktor lain yang juga mempengaruhi konsentrasi SO2 selain PM10.

                - Sumber Polutan: Kedua polutan ini seringkali berasal dari sumber yang sama, seperti pembakaran bahan bakar fosil. Oleh karena itu, wajar jika terdapat hubungan positif di antara keduanya.

                **Hubungan antara TEMP & 03**
                - Tren Positif: Terdapat tren positif yang cukup jelas antara suhu (TEMP) dan konsentrasi ozon (O3). Artinya, semakin tinggi suhu, cenderung semakin tinggi pula konsentrasi ozon.

                - Korelasi Moderat: Korelasi antara suhu dan ozon juga cenderung moderat. Faktor lain seperti intensitas sinar matahari dan keberadaan senyawa organik volatil (VOC) juga dapat mempengaruhi pembentukan ozon.

                - Proses Pembentukan Ozon: Suhu yang tinggi dapat mempercepat reaksi kimia yang menghasilkan ozon di atmosfer.

                **Hubungan antara RAIN & CO**
                - Tren Negatif: Terlihat tren negatif yang cukup jelas antara curah hujan (RAIN) dan konsentrasi karbon monoksida (CO). Artinya, semakin tinggi curah hujan, cenderung semakin rendah konsentrasi CO.

                - Korelasi Moderat: Korelasi antara curah hujan dan CO juga cenderung moderat.

                - Pengenceran Polutan: Curah hujan dapat membantu mengencerkan konsentrasi polutan di udara, termasuk CO. Selain itu, curah hujan juga dapat mempengaruhi aktivitas manusia yang menghasilkan CO, seperti penggunaan kendaraan bermotor.
                """
            )
    elif segment == 'Kadar Polutan':
        ui.table(kadar_polutan)
        with st.expander('Show explanation', expanded=True):
            st.markdown(
                """
                - Rata-rata kadar PM10 tertinggi terdapat pada kota Gucheng
                - Rata-rata kadar SO2 tertinggi terdapat pada kota Nongzhanguan
                - Rata-rata kadar NO2 tertinggi terdapat pada kota Wanliu
                - Rata-rata kadar CO tertinggi terdapat pada kota Wanshouxigong
                - Rata-rata kadar O3 tertinggi terdapat pada kota Huair

                Kolom total kadar_polusi adalah sebuah metrik yang dihitung dengan mengambil rata-rata dari keempat polutan. Ini memberikan kita sebuah angka tunggal yang dapat digunakan untuk membandingkan tingkat polusi antar kota. 
                Semakin tinggi nilai total 'kadar_polusi, semakin tinggi pula tingkat polusi dari kota tersebut.
                """
            )
        # Viusalisasi peringkat kota dengan polutan tertinggi
        with st.expander('Show graph'):

            polutan = air_quality.groupby(by="station").agg({
                "PM10": ["mean"],
                "SO2": ["mean"],
                "NO2": ["mean"],
                "CO": ["mean"],
                "O3": ["mean"]
            })

            # Hitung rata-rata dari semua nilai polutan untuk setiap stasiun
            polutan['total_kadar_polusi'] = polutan.mean(axis=1)

            # Urutkan berdasarkan total_kadar_polusi secara descending
            polutan = polutan.sort_values(by='total_kadar_polusi', ascending=False)

            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x='total_kadar_polusi', y=polutan.index, data=polutan, palette='viridis', ax=ax)
            ax.set_title('Peringkat kota dengan poluatan tertinggi')
            ax.set_xlabel('')
            ax.set_ylabel('Kota')

            # Menambahkan label nilai pada setiap batang
            for i, v in enumerate(polutan['total_kadar_polusi']):
                ax.text(v + 0.02, i, str(round(v, 2)), color='black')

            st.pyplot(fig)

    # Visualisasi rataa-rata tahunan konsentrasi polutan 
    elif segment == 'Tren Musiman':

        air_quality['datetime'] = pd.to_datetime(air_quality['datetime'])
        
        pollutant_means_over_years = air_quality.groupby('datetime')[['SO2', 'NO2', 'O3']].mean()
        # Kelompokkan data berdasarkan tahun dan hitung rata-rata CO
        air_quality['year'] = air_quality['datetime'].dt.year
        rata_rata_tahunan = air_quality.groupby('year')[['CO']].mean()

        # Membuat line plot
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot untuk CO
        ax.plot(rata_rata_tahunan.index, rata_rata_tahunan['CO'], marker='o', label='CO')

        # Memberikan judul dan label sumbu
        ax.set_title('Rata-rata Tahunan Konsentrasi CO')
        ax.set_xlabel('Tahun')
        ax.set_ylabel('Konsentrasi')
        ax.grid(True)

        # Menampilkan plot pada Streamlit
        st.pyplot(fig)


        # Kelompokkan data berdasarkan tahun dan hitung rata-rata polutan
        rata_rata_tahunan = air_quality.groupby(air_quality['datetime'].dt.year)[['PM10', 'SO2', 'NO2', 'O3']].mean()

        # Membuat line plot
        fig, ax = plt.subplots(figsize=(12, 6))

        # Buat plot
        ax.plot(rata_rata_tahunan.index, rata_rata_tahunan['PM10'], marker='o', label='PM10')
        ax.plot(rata_rata_tahunan.index, rata_rata_tahunan['SO2'], marker='o', label='SO2')
        ax.plot(rata_rata_tahunan.index, rata_rata_tahunan['NO2'], marker='o', label='NO2')
        ax.plot(rata_rata_tahunan.index, rata_rata_tahunan['O3'], marker='o', label='O3')

        # Memberikan judul dan label sumbu
        ax.set_title('Rata-rata Tahunan Konsentrasi Polutan Udara')
        ax.set_xlabel('Tahun')
        ax.set_ylabel('Konsentrasi')

        # Menambahkan legend dan grid
        ax.legend()
        ax.grid(True)

        # Menampilkan plot pada Streamlit
        st.pyplot(fig)

        with st.expander('Show explanation', expanded=True):
            st.markdown(
                """
                - Berdasarkan grafik ini, dapat disimpulkan bahwa kualitas udara di wilayah tersebut cenderung memburuk dari tahun ke tahun, terutama disebabkan oleh peningkatan konsentrasi partikel debu halus (PM10).
                Perlu dilakukan penelitian lebih lanjut untuk mengidentifikasi penyebab utama peningkatan PM10 dan mencari solusi untuk memperbaiki kualitas udara.
                """
            )
    elif segment == 'Temperature':
        max_min.drop(['RAIN_MAX', 'RAIN_MIN'], axis=1, inplace=True)
        col1, col2 = st.columns([3,1])
        with col1:
            ui.table(max_min)
        with col2:
            st.metric("Maximum Temperature (°C)", f'{round(max_min.TEMP_MAX.max(),1)}°C')
            st.metric("Minimum Temperature (°C)", f'{round(temp_min,1)}°C') # Ga ngerti kalo pake max_TEMP_MIN.max kenapa keluar nya makah 19.9 
        with st.expander('Show explanation', expanded=True):
            st.markdown(
                """
                - **Suhu Ekstrem**: Kita dapat melihat suhu tertinggi dan terendah yang pernah tercatat di setiap kota. 
                Ini memberikan gambaran tentang rentang suhu yang terjadi di setiap lokasi.
                """
            )
    elif segment == 'Rain Volume':
        max_min.drop(['TEMP_MAX', 'TEMP_MIN'], axis=1, inplace=True)
        col1, col2 = st.columns([3,1])
        with col1:
            ui.table(max_min)
        with col2:
            st.metric("Maximum Rain Volume (mm)", f'{round(max_min.RAIN_MAX.max(),1)}mm')
            st.metric("Average Rain Volume (mm)", f'{round(air_quality.RAIN.mean(),1)}mm')
        with st.expander('Show explanation', expanded=True):
            st.markdown(
                """
                - **Curah Hujan**: Meskipun nilai minimum curah hujan semuanya 0, nilai maksimum memberikan informasi tentang potensi curah hujan tertinggi yang pernah terjadi di setiap kota. Berdasarkan histogram yang di tampilkan di atas yaitu distribusi persebaran RAIN, data curah hujan (RAIN) memiliki distribusi yang sangat miring ke kanan. Ini mengindikasikan bahwa sebagian besar data bernilai 0 atau mendekati 0, dengan sedikit sekali kejadian curah hujan yang tinggi. Kondisi ini cukup umum pada data curah hujan, terutama di daerah dengan iklim kering.
                - **Perbandingan kota**: Kita dapat membandingkan suhu dan curah hujan antara berbagai kota untuk melihat perbedaan iklim di masing-masing lokasi. Misalnya, kita dapat melihat kota mana yang memiliki suhu tertinggi atau curah hujan terbanyak.
                """
            )

elif tabs == 'Conclusion':
    st.markdown(
        """
        ### **Conclusion :book:**

        **Pertanyaan 1**

        **Hubungan antara PM10 & SO2**
        - Tren Positif: Terlihat adanya tren positif yang lemah antara konsentrasi PM10 dan SO2. Artinya, ketika konsentrasi PM10 meningkat, cenderung diikuti oleh peningkatan konsentrasi SO2.

        - Korelasi Moderat: Korelasi antara kedua polutan ini cenderung moderat, tidak terlalu kuat. Hal ini menunjukkan bahwa ada faktor lain yang juga mempengaruhi konsentrasi SO2 selain PM10.

        - Sumber Polutan: Kedua polutan ini seringkali berasal dari sumber yang sama, seperti pembakaran bahan bakar fosil. Oleh karena itu, wajar jika terdapat hubungan positif di antara keduanya.

        **Hubungan antara TEMP & 03**
        - Tren Positif: Terdapat tren positif yang cukup jelas antara suhu (TEMP) dan konsentrasi ozon (O3). Artinya, semakin tinggi suhu, cenderung semakin tinggi pula konsentrasi ozon.

        - Korelasi Moderat: Korelasi antara suhu dan ozon juga cenderung moderat. Faktor lain seperti intensitas sinar matahari dan keberadaan senyawa organik volatil (VOC) juga dapat mempengaruhi pembentukan ozon.

        - Proses Pembentukan Ozon: Suhu yang tinggi dapat mempercepat reaksi kimia yang menghasilkan ozon di atmosfer.

        **Hubungan antara RAIN & CO**
        - Tren Negatif: Terlihat tren negatif yang cukup jelas antara curah hujan (RAIN) dan konsentrasi karbon monoksida (CO). Artinya, semakin tinggi curah hujan, cenderung semakin rendah konsentrasi CO.

        - Korelasi Moderat: Korelasi antara curah hujan dan CO juga cenderung moderat.

        - Pengenceran Polutan: Curah hujan dapat membantu mengencerkan konsentrasi polutan di udara, termasuk CO. Selain itu, curah hujan juga dapat mempengaruhi aktivitas manusia yang menghasilkan CO, seperti penggunaan kendaraan bermotor.
        
        **Pertanyaan 2** 

        Berdasarkan tabel kadar polutan :

        - Rata-rata kadar PM10 tertinggi terdapat pada kota Gucheng
        - Rata-rata kadar SO2 tertinggi terdapat pada kota Nongzhanguan
        - Rata-rata kadar NO2 tertinggi terdapat pada kota Wanliu
        - Rata-rata kadar CO tertinggi terdapat pada kota Wanshouxigong
        - Rata-rata kadar O3 tertinggi terdapat pada kota Huair

        Kolom total kadar_polusi adalah sebuah metrik yang dihitung dengan mengambil rata-rata dari keempat polutan. Ini memberikan kita sebuah angka tunggal yang dapat digunakan untuk membandingkan tingkat polusi antar kota. 
        Semakin tinggi nilai total 'kadar_polusi, semakin tinggi pula tingkat polusi dari kota tersebut.

        **Pertanyaan 3**

        - Berdasarkan grafik pada tabel tren musiman, dapat disimpulkan bahwa kualitas udara di wilayah tersebut cenderung memburuk dari tahun ke   tahun, terutama disebabkan oleh peningkatan konsentrasi partikel debu halus (PM10).
        Perlu dilakukan penelitian lebih lanjut untuk mengidentifikasi penyebab utama peningkatan PM10 dan mencari solusi untuk memperbaiki kualitas udara.
        
        **Pertanyaan 4** 

        - Bisa kita lihat pada Temperatur & curah hujan di berbagai kota / tabel temperatur pada dashboard, 
        temperature maximum 41.6°C pada kota Gucheng. Sedangkan minimum nya -15.6°C pada kota yang sama yaitu Gucheng.

        **Pertanyaan 5**

        Curah hujan tertinggi berada di kota Aotizhongxin dengan maximum volume 72.5mm.

        - **Curah Hujan**: Meskipun nilai minimum curah hujan semuanya 0, nilai maksimum memberikan informasi tentang potensi curah hujan tertinggi yang pernah terjadi di setiap kota. Berdasarkan histogram yang di tampilkan di atas yaitu distribusi persebaran RAIN, data curah hujan (RAIN) memiliki distribusi yang sangat miring ke kanan. 
        Ini mengindikasikan bahwa sebagian besar data bernilai 0 atau mendekati 0, dengan sedikit sekali kejadian curah hujan yang tinggi. Kondisi ini cukup umum pada data curah hujan, terutama di daerah dengan iklim kering.
        - **Perbandingan kota**: Kita dapat membandingkan suhu dan curah hujan antara berbagai kota untuk melihat perbedaan iklim di masing-masing lokasi. Misalnya, kita dapat melihat kota mana yang memiliki suhu tertinggi atau curah hujan terbanyak. 
        """
    )

st.caption('*Copyright © 2024 Dasboard.*')
