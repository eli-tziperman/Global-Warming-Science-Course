# 1) make a folder and cd into it
mkdir -p houston_iah_meteostat && cd $_

# 2) download all years (brace expansion)
for y in {2000..2024}; do
  curl -L "https://data.meteostat.net/daily/${y}/72243.csv.gz" -o "${y}.csv.gz"
done

# 3) decompress
gunzip *.gz

# 4) keep header from the first file, then append others without headers
cat 2000.csv > houston_IAH_daily_2000_2024.csv
for f in {2001..2024}.csv; do
  tail -n +2 "$f" >> houston_IAH_daily_2000_2024.csv
done
