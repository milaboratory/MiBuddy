import pandas as pd
import yaml
import re
import argparse

def meta2YAML(input_file, output_prefix):
    file=pd.read_table(input_file)
    YAML=[]
    for R, data in file.groupby(['R1', 'R2']):
        run={}
        run['R1']=R[0]
        run['R2']=R[1]
        run['cDNA_library_type']=data.reset_index().ix[[0],'cDNA_library_type'][0]
        run['date']=data.reset_index().ix[[0],'Date'][0]
        run['place']=data.reset_index().ix[[0],'Place'][0]
        run['sequencer']=data.reset_index().ix[[0],'Sequencer'][0]
        run['type']=data.reset_index().ix[[0],'Type'][0]
        migec = [col for col in data.columns if 'migec.' in col] #Selecting columns that contain "migec." pattern
        run['migec_parametrs']={}
        for i in migec:
            run['migec_parametrs'][re.search('migec\.(.*)',i).group(1)]=str(data.reset_index().ix[[0],i][0])
        mixcr = [col for col in data.columns if 'mixcr.' in col] #Selecting columns that contain "mixcr." pattern
        run['mixcr_parametrs']={}
        for i in mixcr:
            run['mixcr_parametrs'][re.search('mixcr\.(.*)',i).group(1)]=str(data.reset_index().ix[[0],i][0])
        run['patterns']=[]
        for pattern,samples in data.reset_index().groupby(['pattern.left','pattern.right']):
            patterns={}
            patterns['left']=pattern[0]
            patterns['right']=pattern[1]
            patterns['samples']=[]
            for barcodes,metadata in samples.groupby(['sample.G1_barcode','sample.G2_barcode']):
                sample={}
                sample_data = [col for col in metadata.columns if 'sample.' in col]
                for i in sample_data:
                    sample[re.search('sample\.(.*)',i).group(1)]=str(metadata.reset_index().ix[[0],i][0])
                patterns['samples'].append(sample)
            run['patterns'].append(patterns)
        YAML.append(run)
    with open(output_prefix+'_'+'metadata.yml', 'w') as outfile:
        yaml.dump(YAML, outfile, default_flow_style=False)

def main(args):
    meta2YAML(args.metadata_file, args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata_file", help="Specify metadata file in tab delimeted format")
    parser.add_argument("output", help="Specify prefix for output file")

    try:
        args = parser.parse_args()
    except SystemExit:
        print("Too few arguments provided")
    main(args)