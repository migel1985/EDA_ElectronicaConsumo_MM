import numpy as np # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
import matplotlib.ticker as mtick # type: ignore
import matplotlib.dates as mdates # type: ignore
import pandas as pd # type: ignore
import itertools # type: ignore

class Graficos:

    def hipotesis1(self, pDataSet):
        print("paso por hipotesis1")
        hipoGraph = Graficos()
        dataSetHpy1a = pDataSet[pDataSet['Unit Price'].notna() & (pDataSet['Unit Price'] > 0)]
        dataSetHpy1a = dataSetHpy1a.groupby(['SKU'], as_index=False)['Unit Price'].max()
        dataSetHpy1a = dataSetHpy1a.sort_values(by='Unit Price', ascending=False)
        dataSetHpy1b = pDataSet[pDataSet['Unit Price'].notna() & (pDataSet['Unit Price'] > 0)]
        dataSetHpy1b = dataSetHpy1b.groupby(['SKU'], as_index=False)['Rating'].mean()
        dataSetHpy1b = dataSetHpy1b.sort_values(by='Rating', ascending=False)
        dataSetHpy1 = pd.merge(
            dataSetHpy1a[['SKU', 'Unit Price']], 
            dataSetHpy1b[['SKU', 'Rating']], 
            on='SKU', 
            how='inner'
        )
        dataSetHpy1 = dataSetHpy1.sort_values(by='Unit Price', ascending=False)
        fig, ax1 = plt.subplots(figsize=(10,6))
        ax2 = ax1.twinx()
        ax1.bar(dataSetHpy1['SKU'], dataSetHpy1['Unit Price'], color='lightblue', label='Precio (€)')
        ax2.plot(dataSetHpy1['SKU'], dataSetHpy1['Rating'], color='darkred', marker='o', label='Rating')
        ax1.set_xlabel('SKU')
        ax1.set_ylabel('Precio (€)')
        ax2.set_ylabel('Rating', color='darkred')
        plt.title("Precio vs Valoración media por producto")
        plt.xticks(rotation=45)
        plt.tight_layout()
        #plt.show()
        fig.savefig("src/data/images/hipotesis1.png")


    def hipotesis2(self, pDataSet):
        dataSetHpy2 = pDataSet.copy()
        bins = [0, 29, 59, 120]
        labels = ['Joven', 'Adulto', 'Mayor']
        dataSetHpy2['AgeGroup'] = pd.cut(dataSetHpy2['Age'], bins=bins, labels=labels, right=True)
        dataSetHpy2 = dataSetHpy2.sort_values(by='AgeGroup', ascending=False)
        bins = [0, 5, 10, 20, 50, 100, 500]  # rangos de precio
        fig, ax = plt.subplots()
        sns.histplot(
            data=dataSetHpy2,
            x='Unit Price',
            hue='AgeGroup',
            bins=bins,
            multiple='dodge',
            palette='coolwarm',
            edgecolor='black',
            ax = ax
        )
        
        fig.savefig("src/data/images/hipotesis2.png", bbox_inches='tight')

    def hipotesis3(self, pDataSet):
        dataSetHpy3 = pDataSet.loc[pDataSet["Order Status"] == "Completed"]
        dataSetHpy3 = pDataSet[pDataSet['Total Price'].notna() & pDataSet['Purchase Date'].notna()]
        dataSetHpy3['Purchase Date'] = pd.to_datetime(dataSetHpy3['Purchase Date'])
        dataSetHpy3['Month'] = dataSetHpy3['Purchase Date'].dt.to_period('M').astype(str)
        sales_by_month = (
            dataSetHpy3
            .groupby(['Month', 'Loyalty Member'], as_index=False)['Total Price']
            .sum()
            .sort_values('Month')
        )
        hp3ComprasFieles = sales_by_month[sales_by_month["Loyalty Member"] == "Yes"][["Month", "Total Price"]]
        hp3ComprasNoFieles = sales_by_month[sales_by_month["Loyalty Member"] == "No"][["Month", "Total Price"]]
        hp3ComprasFieles['tipo'] = 'Fidelizados'
        hp3ComprasNoFieles['tipo'] = 'No fidelizados'
        df_total = pd.concat([hp3ComprasFieles, hp3ComprasNoFieles])
        df_pivot = df_total.pivot_table(
            index='Month',
            columns='tipo',
            values='Total Price',
            aggfunc='sum'
        ).sort_index()
        plt.figure(figsize=(11,6))
        ax = df_pivot.plot.area(alpha=0.35, linewidth=2, figsize=(11,6))
        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('{x:,.0f} €'))
        ax.set_title('Ventas mensuales: Fidelizados vs No fidelizados', fontsize=12)
        ax.set_xlabel('Mes')
        ax.set_ylabel('Ventas (€)')
        plt.grid(axis='y', linestyle='--', alpha=0.4)
        plt.tight_layout()
        fig = ax.get_figure()
        fig.savefig("src/data/images/hipotesis3.png", bbox_inches='tight')

    def hipotesis4(self, pDataSet):
        abandonedHy4 = pDataSet[pDataSet['Order Status'] == "Abandoned cart"].copy()
        abandonedHy4['Purchase Date'] = pd.to_datetime(abandonedHy4['Purchase Date'])
        abandonedHy4['Month'] = abandonedHy4['Purchase Date'].dt.to_period('M').astype(str)
        abandonedHy4['tipo'] = abandonedHy4['Loyalty Member'].map({'Yes':'Fidelizados', 'No':'No fidelizados'})
        abandoned_by_month = (
            abandonedHy4.groupby(['Month','tipo'])
            .size()
            .reset_index(name='Abandoned Count')
            .sort_values('Month')
        )
        plt.figure(figsize=(12,6))
        sns.lineplot(
            data=abandoned_by_month,
            x='Month',
            y='Abandoned Count',
            hue='tipo',
            marker='o',
            lw=2
        )
        plt.title('Evolución de carritos abandonados por tipo de cliente', fontsize=14, weight='bold')
        plt.xlabel('Mes')
        plt.ylabel('Número de carritos abandonados')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend(title='Tipo de cliente')
        plt.tight_layout()
        plt.savefig("src/data/images/hipotesis4.png", bbox_inches='tight')

        
    def hipotesis5(self, pDataSet):
        fidelizadosHyp5 = pDataSet[pDataSet['Loyalty Member'] == 'Yes'].copy()
        fidelizadosHyp5['Purchase Date'] = pd.to_datetime(fidelizadosHyp5['Purchase Date'])
        fidelizadosHyp5['Month'] = fidelizadosHyp5['Purchase Date'].dt.to_period('M').astype(str)
        fidelizados_status = fidelizadosHyp5[fidelizadosHyp5['Order Status'].isin(['Completed', 'Cancelled'])]
        pedidos_por_mes = (
            fidelizados_status.groupby(['Month','Order Status'])
            .size()
            .reset_index(name='Count')
        )
        plt.figure(figsize=(12,6))
        sns.lineplot(
            data=pedidos_por_mes,
            x='Month',
            y='Count',
            hue='Order Status',
            marker='o',
            lw=2
        )
        plt.title('Pedidos de clientes fidelizados por mes: Completados vs Cancelados', fontsize=14, weight='bold')
        plt.xlabel('Mes')
        plt.ylabel('Número de pedidos')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.legend(title='Estado del pedido')
        plt.tight_layout()
        plt.savefig("src/data/images/hipotesis5.png", bbox_inches='tight')

    def hipotesis6(self, pDataSet):
        pDataSet['Purchase Date'] = pd.to_datetime(pDataSet['Purchase Date'])
        pDataSet['Month'] = pDataSet['Purchase Date'].dt.to_period('M').astype(str)
        estados = ['Completed', 'Cancelled', 'Abandoned cart']
        pedidos = pDataSet[pDataSet['Order Status'].isin(estados)]
        pedidos_por_mes = (
            pedidos.groupby(['Month','Order Status'])
            .size()
            .reset_index(name='Count')
        )
        all_months = sorted(pedidos_por_mes['Month'].unique())
        full_index = pd.DataFrame(list(itertools.product(all_months, estados)), columns=['Month','Order Status'])
        pedidos_por_mes = full_index.merge(pedidos_por_mes, on=['Month','Order Status'], how='left')
        pedidos_por_mes['Count'] = pedidos_por_mes['Count'].fillna(0)
        pedidos_pivot = pedidos_por_mes.pivot(index='Month', columns='Order Status', values='Count').fillna(0)
        pedidos_pivot['Abandon_Rate'] = (pedidos_pivot['Cancelled'] + pedidos_pivot['Abandoned cart']) / (
            pedidos_pivot['Completed'] + pedidos_pivot['Cancelled'] + pedidos_pivot['Abandoned cart']
        )
        plt.figure(figsize=(12,6))
        sns.lineplot(
            data=pedidos_pivot.reset_index(),
            x='Month',
            y='Abandon_Rate',
            marker='o',
            lw=2
        )
        plt.axhline(0.5, color='red', linestyle='--', label='50%')
        plt.title('Tasa de abandono de carritos por mes', fontsize=14, weight='bold')
        plt.ylabel('Tasa de abandono')
        plt.xlabel('Mes')
        plt.xticks(rotation=45)
        plt.ylim(0,1)
        plt.gca().yaxis.set_major_formatter(lambda y, _: f'{y:.0%}')  # Formato porcentaje
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.legend()
        plt.tight_layout()
        plt.savefig("src/data/images/hipotesis6.png", bbox_inches='tight')

    def hipotesis7(self, pDataSet):
        pDataSet['Purchase Date'] = pd.to_datetime(pDataSet['Purchase Date'])
        pDataSet['Month'] = pDataSet['Purchase Date'].dt.to_period('M').astype(str)
        filtered_df = pDataSet[pDataSet['Shipping Type'].isin(['Express', 'Standard', 'Same Day'])].copy()
        orders_by_month = (
            filtered_df.groupby(['Month','Shipping Type'])
            .size()
            .reset_index(name='Count')
            .sort_values('Month')
        )
        plt.figure(figsize=(12,6))
        sns.lineplot(
            data=orders_by_month,
            x='Month',
            y='Count',
            hue='Shipping Type',
            marker='o',
            lw=2
        )
        plt.title('Evolución de pedidos por tipo de envío por mes', fontsize=14, weight='bold')
        plt.xlabel('Mes')
        plt.ylabel('Número de pedidos')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.4)
        plt.legend(title='Tipo de envío', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig("src/data/images/hipotesis7.png", bbox_inches='tight')