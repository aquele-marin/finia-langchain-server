import "./styles.css";

interface StockChartProps {
    stocks: string[];
}

const StockComponent = ({ stocks }: StockChartProps) => {
    return <div>stocksss: {stocks}</div>;
};

export default {
    stock: StockComponent,
};
