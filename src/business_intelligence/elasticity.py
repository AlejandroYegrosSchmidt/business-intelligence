import pandas as pd

class config_table:
    def __init__(self, date_col,articule_cod_col, quantity_col, sales_col):
        self.date = date_col
        self.articule = articule_cod_col
        self.price_col = sales_col
        self.quantity_col = quantity_col

    def calculate_elasticity(self,dataframe=None ,cod_art=None, q_range=5):
        """
        Calculate the price elasticity of demand.
        """
        if dataframe.empty:
            raise ValueError('Se requiere un DataFrame')

        # Select the columns of interest
        required_columns = [self.date,self.articule,self.price_col, self.quantity_col]
        for col in required_columns:
            if col not in dataframe.columns: 
                raise ValueError(f'La columna {col} no se encuentra en el dataframe')
        dataframe = dataframe[required_columns]

        # Filter the data by the articule
        if cod_art is not None:
            dataframe = dataframe[dataframe[self.articule] == cod_art]
            if dataframe.empty:
                raise ValueError(f'No se encontro el articulo cod {cod_art}')

        # Convertir las columnas a tipo numerico 
        dataframe[self.price_col] = pd.to_numeric(dataframe[self.price_col], errors='coerce')
        dataframe[self.quantity_col] = pd.to_numeric(dataframe[self.quantity_col], errors='coerce')

        # Eliminar filas con nan en columnas clave
        dataframe.dropna(subset=[self.price_col, self.quantity_col], inplace=True)

        # create a new column for the single price
        dataframe['range_price_avg'] = (dataframe[self.price_col] / dataframe[self.quantity_col]).round(0)

        # remove the rows with zero price or quantity
        dataframe = dataframe[(dataframe['range_price_avg'] > 0) & (dataframe[self.quantity_col] > 0)]

        # Calculate the total 
        prices_unique = dataframe['range_price_avg'].sort_values(ascending=True).unique()
        demand = []
        for price in prices_unique:
            demand.append(dataframe[dataframe['range_price_avg'] == price][self.quantity_col].sum())

        # Discritize the singel prices
        ranges = pd.DataFrame({'range_price_avg':prices_unique})
        ranges = pd.qcut(ranges['range_price_avg'], q=q_range).unique()
        
        # Create a table with the demand for each price range
        table = pd.DataFrame({'range_price_avg':prices_unique, 'demand':demand})
        for range in ranges:
            for index, row in table.iterrows():
                if row['range_price_avg'] in range:
                    table.loc[index, 'range_price'] = range
        table = table.groupby('range_price').agg({'demand':'sum'}).reset_index() 

        # Calculate the elasticity of demand for each price range
        table['range_price_avg'] = table['range_price'].apply(lambda x: x.mid).round(0)
        table = table[['range_price','range_price_avg','demand']]
        table['var_range_price_avg'] = table['range_price_avg'].pct_change().abs()
        table['var_demand'] = table['demand'].pct_change().abs()
        table['elasticity'] = (table['var_demand'] / table['var_range_price_avg']).abs()

        table = pd.DataFrame(table)
        return table
