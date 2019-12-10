from bin import Binner
chrom_sizes={"chr1": 249250621, "chr10": 135534747, "chr11": 135006516, "chr12": 133851895, "chr13": 115169878, "chr14": 107349540, "chr15": 102531392, "chr16": 90354753, "chr17": 81195210, "chr18": 78077248, "chr19": 59128983, "chr2": 243199373, "chr20": 63025520, "chr21": 48129895, "chr22": 51304566, "chr3": 198022430, "chr4": 191154276, "chr5": 180915260, "chr6": 171115067, "chr7": 159138663, "chr8": 146364022, "chr9": 141213431}
b = Binner(chrom_sizes, 10000)
print(b.get_bin('chr1',    9720005))
print(b.get_bin('chr2',  201230005))
print(b.get_bin('chr2',  208660005))
print(b.get_bin('chr15',  66610005))
print(b.get_bin('chr17',  77140005))
