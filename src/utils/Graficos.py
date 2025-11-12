import numpy as np # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
import matplotlib.ticker as mtick # type: ignore
import matplotlib.dates as mdates # type: ignore
import pandas as pd # type: ignore
import itertools # type: ignore

class Graficos:

    def hipotesis1(self, pDataSet):
        #preparamos los data frames de precios de artículos, limpiamos los datos para que no tome en cuenta productos con precios Nulos o productos con precio 0.
        dataSetHpy1a = pDataSet[pDataSet['Unit Price'].notna() & (pDataSet['Unit Price'] > 0)]
        dataSetHpy1a = dataSetHpy1a.groupby(['SKU'], as_index=False)['Unit Price'].max()
        dataSetHpy1a = dataSetHpy1a.sort_values(by='Unit Price', ascending=False)
        dataSetHpy1b = pDataSet[pDataSet['Unit Price'].notna() & (pDataSet['Unit Price'] > 0)]
        dataSetHpy1b = dataSetHpy1b.groupby(['SKU'], as_index=False)['Rating'].mean()
        dataSetHpy1b = dataSetHpy1b.sort_values(by='Rating', ascending=False)
        # Mergeamos los dataframes para así meterlos en el código del gráfico de barras / lineas, con inner aseguramos que nos quedamos con los datos de ambos dataframes que tienen rating y precio.
        dataSetHpy1 = pd.merge(
            dataSetHpy1a[['SKU', 'Unit Price']], 
            dataSetHpy1b[['SKU', 'Rating']], 
            on='SKU', 
            how='inner'
        )
        # Ordenamos por precio, es más significativo que la evolución del Rating respecto a los precios.
        dataSetHpy1 = dataSetHpy1.sort_values(by='Unit Price', ascending=False)
        fig, ax1 = plt.subplots(figsize=(10,6))
        ax2 = ax1.twinx() # Creamos el segundo eje (vertical) para el Rating, es decir, ax1 --> Izquierda precio, ax2 --> Derecha Rating.
        ax1.bar(dataSetHpy1['SKU'], dataSetHpy1['Unit Price'], color='lightblue', label='Precio (€)')
        ax2.plot(dataSetHpy1['SKU'], dataSetHpy1['Rating'], color='darkred', marker='o', label='Rating')
        #ponemos los labels de eje X y ejes Y's
        ax1.set_xlabel('SKU')
        ax1.set_ylabel('Precio (€)')
        ax2.set_ylabel('Rating', color='darkred')
        plt.title("Precio vs Valoración media por producto")
        plt.xticks(rotation=45)
        # Hago que los elementos del gráfico queden bien distribuidos y visibles
        plt.tight_layout()
        fig.savefig("src/data/images/hipotesis1.png")


    def hipotesis2(self, pDataSet):
        # Me copio el dataset inicial a uno local para poder toquetearlo sin modificar el primero. Es verdad que se pasa como parámetro y no se devuelve así que los
        # lo que hagamos aquí no tendrá efecto en el origen, pero por salvarme en salud lo he decidido así.
        dataSetHpy2 = pDataSet.copy()
        # Esto lo he descubierto con Ayuda de IA. La forma de subdividir las edades por rangos de edad, que se van a usar más adelante.
        bins = [0, 29, 59, 120]
        labels = ['Joven', 'Adulto', 'Mayor']
        # Con cut de pandas, dividimos los datos de la Edad en una agrupación de "Grupo de edad", los bins y labels tienen que ser los mismos.
        # El parámetro right=True indica que el límite superior del intervalo está incluido (por ejemplo, 29 entra en “Joven”).
        dataSetHpy2['AgeGroup'] = pd.cut(dataSetHpy2['Age'], bins=bins, labels=labels, right=True)
        dataSetHpy2 = dataSetHpy2.sort_values(by='AgeGroup', ascending=False)
        # Creamos el lienzo
        fig, ax = plt.subplots()
        # creamos el histograma
        binsprecios = [0, 50, 500, 1500]  # rangos de precio para agrupar los valores en el Eje X. Tres grupos de precios: 0 - 50, 51-500, 501 - 1500
        sns.histplot(
            data=dataSetHpy2,
            x='Unit Price',
            hue='AgeGroup',
            multiple='dodge',
            bins=binsprecios,
            palette='coolwarm',
            edgecolor='black',
            ax = ax
        )
        
        fig.savefig("src/data/images/hipotesis2.png", bbox_inches='tight')

    def hipotesis3(self, pDataSet):
        # Nos quedamos con los datos de los registros que han sido completados, no nos interesa el resto
        dataSetHpy3 = pDataSet.loc[pDataSet["Order Status"] == "Completed"]
        dataSetHpy3 = pDataSet[pDataSet['Total Price'].notna() & pDataSet['Purchase Date'].notna()]
        # Queremos mostrar la gráfica por evolución temporal, así que preparo el mes y año
        dataSetHpy3['Purchase Date'] = pd.to_datetime(dataSetHpy3['Purchase Date'])
        dataSetHpy3['Month'] = dataSetHpy3['Purchase Date'].dt.to_period('M').astype(str)
        # Agrupamos por mes / año y hacemos la suma del precio total para ver la venta total. Se entiende que los pedidos son uniproducto multicantidad pedida
        sales_by_month = (
            dataSetHpy3
            .groupby(['Month', 'Loyalty Member'], as_index=False)['Total Price']
            .sum()
            .sort_values('Month')
        )
        # Dividimos el df en ventas de clientes fidelizados y clientes no fidelizados.
        hp3ComprasFieles = sales_by_month[sales_by_month["Loyalty Member"] == "Yes"][["Month", "Total Price"]]
        hp3ComprasNoFieles = sales_by_month[sales_by_month["Loyalty Member"] == "No"][["Month", "Total Price"]]
        hp3ComprasFieles['tipo'] = 'Fidelizados'
        hp3ComprasNoFieles['tipo'] = 'No fidelizados'
        # Concatenamos las dos tablas porque queremos meses de ambos que no estén en el contrario, por eso no hacemos un inner por ejemplo.
        df_total = pd.concat([hp3ComprasFieles, hp3ComprasNoFieles])
        #Creamos el pivote para reorganizar los datos y que el gráfico de areas lo entienda mejor y lo calce
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
        # Nos quedamos con los datos de los carritos abandonados.
        abandonedHy4 = pDataSet[pDataSet['Order Status'] == "Abandoned cart"].copy()
        # Convertimos como en otros gráficos la fecha en rango de meses y agrupamos los datos por mes.
        abandonedHy4['Purchase Date'] = pd.to_datetime(abandonedHy4['Purchase Date'])
        abandonedHy4['Month'] = abandonedHy4['Purchase Date'].dt.to_period('M').astype(str)
        abandonedHy4['tipo'] = abandonedHy4['Loyalty Member'].map({'Yes':'Fidelizados', 'No':'No fidelizados'})
        abandoned_by_month = (
            abandonedHy4.groupby(['Month','tipo'])
            .size()
            .reset_index(name='Abandoned Count')
            .sort_values('Month')
        )
        # generamos figura de gráfico y lo pintamos.
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
        # Nos quedamos con la información de los clientes fidelizados.
        fidelizadosHyp5 = pDataSet[pDataSet['Loyalty Member'] == 'Yes'].copy()
        # agrupamos los datos por mes - año y agrupamos los datos de los pedidos completados y cancelados para analizar su evolución.
        fidelizadosHyp5['Purchase Date'] = pd.to_datetime(fidelizadosHyp5['Purchase Date'])
        fidelizadosHyp5['Month'] = fidelizadosHyp5['Purchase Date'].dt.to_period('M').astype(str)
        fidelizados_status = fidelizadosHyp5[fidelizadosHyp5['Order Status'].isin(['Completed', 'Cancelled'])]
        pedidos_por_mes = (
            fidelizados_status.groupby(['Month','Order Status'])
            .size()
            .reset_index(name='Count')
        )
        # Creamos gráfico de lineas con la evolución de cancelaciones y completados.
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
        # Convertimos la fecha en mes / año
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
        # Calculamos el % de los pedidos Cancelados y Abandonados
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
        # Como en los últimos gráficos saco los meses / años
        pDataSet['Purchase Date'] = pd.to_datetime(pDataSet['Purchase Date'])
        pDataSet['Month'] = pDataSet['Purchase Date'].dt.to_period('M').astype(str)
        filtered_df = pDataSet[pDataSet['Shipping Type'].isin(['Express', 'Standard', 'Same Day'])].copy()
        # me traigo los datos de los tipos de envíos Express, Standard, y Same Day
        orders_by_month = (
            filtered_df.groupby(['Month','Shipping Type'])
            .size()
            .reset_index(name='Count')
            .sort_values('Month')
        )
        plt.figure(figsize=(12,6))
        # generamos el gráfico
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

    def hipotesis8(self, pDataSet):
        # Por grupo de edad 
        datasetHyp8 = pDataSet.copy()
        bins = [0, 29, 59, 120]
        labels = ['Joven', 'Adulto', 'Mayor']
        datasetHyp8['AgeGroup'] = pd.cut(datasetHyp8['Age'], bins=bins, labels=labels, right=True)
        # Sacamos el gráfico con los métodos de pago agrupados por rango de edad
        plt.figure(figsize=(12,6))
        sns.countplot(data=datasetHyp8, x='AgeGroup', hue='Payment Method')
        plt.title("Forma de pago según grupo de edad")
        plt.xlabel("Grupo de edad")
        plt.ylabel("Número de clientes")
        plt.savefig("src/data/images/hipotesis8.png", bbox_inches='tight')