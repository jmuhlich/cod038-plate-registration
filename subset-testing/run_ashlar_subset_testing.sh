p7_1=/n/files/HiTS/lsp-data/screening-dev/Coralie/20231207-DDD-longTerm-Cy1-7d/2023-12-07/28923/TimePoint_1
p7_2=/n/files/HiTS/lsp-data/screening-dev/Coralie/20231213-DDD-longTerm-Cy2-3d/20231213-DDD-longTerm-Cy2-7d/2023-12-13/28963/TimePoint_1

p7w_1=/n/files/HiTS/lsp-data/screening-dev/Coralie/20231207-DDD-longTerm-Cy1-7d-w/2023-12-07/28916/TimePoint_1
p7w_2=/n/files/HiTS/lsp-data/screening-dev/Coralie/20231213-DDD-longTerm-Cy2-3d/20231213-DDD-longTerm-Cy2-7d-w/2023-12-14/28964/TimePoint_1

wells='E03 F03 G03'

for s in p7 p7w; do
    for w in $wells; do
        vp1="${s}_1"
        vp2="${s}_2"
        fsargs="pattern={exp}_${w}_s{series}_w{channel:1}{uuid:36}.tif|width=5|height=5|overlap=0.05"
        echo -n "env OMP_NUM_THREADS=1 ashlar"
        echo -n " 'fileseries|${!vp1}|${fsargs}'"
        echo -n " 'fileseries|${!vp2}|${fsargs}'"
        echo -n " --filter-sigma 1"
        echo -n " --stitch-alpha 0.5"
        echo -n " -m 20"
        #echo -n " --output-channel 0"
        echo -n " --report report_${s}_${w}.pdf"
        echo -n " -o ${s}_${w}.ome.tif"
        echo
    done
done

