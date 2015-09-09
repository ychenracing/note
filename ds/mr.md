##单表关联##
输入数据如下，第一行为表头，要求输出grandchild grandparent

```
child parent
Tom Lucy
Tom Jack
Jone Lucy
Jone Jack
Lucy Mary
Lucy Ben
Jack Alice
Jack Jesse
Terry Alice
Terry Jesse
Philip Terry
Philip Alma
Mark Terry
Mark Alma
```

要求输出：

```
grandchild grandparent
Tom Alice
Tom Jesse
Jone Alice
Jone Jesse
Tom Ben
Tom Mary
Jone Ben
Jone Mary
Philip Alice
Philip Jesse
Mark Alice
Mark Jesse
```

代码如下：

```java
package wordcount;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class GrandChildParent {

    public static class GrandMapper extends Mapper<Object, Text, Text, Text> {

        private static Text keyText   = new Text();
        private static Text valueText = new Text();

        @Override
        public void map(Object key, Text value, Context context) throws IOException,
                                                                InterruptedException {
            String line = value.toString();
            if (!line.startsWith("child")) {
                String[] values = line.split("\\s+");
                keyText.set(values[1]);
                valueText.set("1+" + values[0] + "+" + values[1]);
                context.write(keyText, valueText);

                keyText.set(values[0]);
                valueText.set("2+" + values[0] + "+" + values[1]);
                context.write(keyText, valueText);
            }
        }
    }

    public static class GrandReducer extends Reducer<Text, Text, Text, Text> {

        private static int  linenum   = 0;
        private static Text keyText   = new Text();
        private static Text valueText = new Text();

        @Override
        public void reduce(Text key, Iterable<Text> values, Context context) throws IOException,
                                                                            InterruptedException {
            if (linenum == 0) {
                keyText.set("grandchild");
                valueText.set("grandparent");
                context.write(keyText, valueText);
                linenum++;
            }

            List<String> grandchildList = new ArrayList<String>();
            List<String> grandparentList = new ArrayList<String>();

            for (Text grandValue : values) {
                String[] grandValueItems = grandValue.toString().split("\\+");
                if (grandValueItems[0].equals("1")) {
                    grandchildList.add(grandValueItems[1]);
                } else {
                    grandparentList.add(grandValueItems[2]);
                }
            }

            // 笛卡儿积
            if (!grandchildList.isEmpty() && !grandparentList.isEmpty()) {
                for (String grandchild : grandchildList) {
                    for (String grandparent : grandparentList) {
                        keyText.set(grandchild);
                        valueText.set(grandparent);
                        context.write(keyText, valueText);
                    }
                }
            }
        }
    }

    public static void main(String[] args) throws IOException, InterruptedException,
                                          ClassNotFoundException {

        Configuration conf = new Configuration();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        if (otherArgs.length < 2) {
            System.err.println("Usage: wordcount.GrandChildParent <in> <out>");
            System.exit(2);
        }
        Job job = Job.getInstance(conf, "single table join");
        job.setJarByClass(GrandChildParent.class);
        job.setMapperClass(GrandMapper.class);
        job.setReducerClass(GrandReducer.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        for (int i = 0; i < otherArgs.length - 1; ++i) {
            FileInputFormat.addInputPath(job, new Path(otherArgs[i]));
        }
        FileOutputFormat.setOutputPath(job, new Path(otherArgs[otherArgs.length - 1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }

}
```

##多表关联##
输入数据如下，第一行为表头，要求输出factoryname addressname

```
factoryname addressed
Beijing Red Star 1
Shenzhen Thunder 3
Guangzhou Honda 2
Beijing Rising 1
Guangzhou Development Bank 2
Tencent 3
Bank of Beijing 1
```

```
addressID addressname
1 Beijing
2 Guangzhou
3 Shenzhen
4 Xian
```

要求输出如下：

```
factoryname addressname
Bank of Beijing Beijing
Beijing Red Star Beijing
Beijing Rising Beijing
Guangzhou Development Bank Guangzhou
Guangzhou Honda Guangzhou
Shenzhen Thunder	Shenzhen
Tencent Shenzhen
```

代码如下：

```java
package wordcount;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class FactoryAddress {

    public static class FactoryAddressMapper extends Mapper<Object, Text, IntWritable, Text> {

        private static IntWritable  keyInt         = new IntWritable();
        private static Text         valueText      = new Text();
        private static final String START_WITH_NUM = "^\\d+\\s.*";
        private static final String END_WITH_NUM   = ".*\\s(\\d)+$";

        @Override
        public void map(Object key, Text value, Context context) throws IOException,
                                                                InterruptedException {
            String line = value.toString();
            if (!line.startsWith("factoryname") && !line.startsWith("addressID")) {

                if (line.matches(START_WITH_NUM)) {
                    int firstSpaceIndex = line.indexOf(" ");
                    String number = line.substring(0, firstSpaceIndex);
                    String address = line.substring(firstSpaceIndex + 1);
                    keyInt.set(Integer.parseInt(number));
                    valueText.set("1+" + address);
                    context.write(keyInt, valueText);
                    return;
                }

                if (line.matches(END_WITH_NUM)) {
                    int lastSpaceIndex = line.lastIndexOf(" ");
                    String number = line.substring(lastSpaceIndex + 1);
                    String factory = line.substring(0, lastSpaceIndex);
                    keyInt.set(Integer.parseInt(number));
                    valueText.set("2+" + factory);
                    context.write(keyInt, valueText);
                }
            }
        }
    }

    public static class FactoryAddressReducer extends Reducer<IntWritable, Text, Text, Text> {

        private static int  linenum   = 0;
        private static Text keyText   = new Text();
        private static Text valueText = new Text();

        @Override
        public void reduce(IntWritable key, Iterable<Text> values, Context context)
                                                                                   throws IOException,
                                                                                   InterruptedException {
            if (linenum == 0) {
                keyText.set("factoryname");
                valueText.set("addressname");
                context.write(keyText, valueText);
                linenum++;
            }

            List<String> factorynameList = new ArrayList<String>();
            String addressname = null;
            for (Text valueItem : values) {
                String value = valueItem.toString();
                if (value.startsWith("1")) {
                    addressname = value.substring(value.indexOf("+") + 1);
                } else if (value.startsWith("2")) {
                    String factoryname = value.substring(value.indexOf("+") + 1);
                    factorynameList.add(factoryname);
                }
            }

            for (String factoryname : factorynameList) {
                keyText.set(factoryname);
                valueText.set(addressname);
                context.write(keyText, valueText);
            }

        }
    }

    public static void main(String[] args) throws IOException, InterruptedException,
                                          ClassNotFoundException {

        Configuration conf = new Configuration();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        if (otherArgs.length < 2) {
            System.err.println("Usage: wordcount.FactoryAddress <in>... <out>");
            System.exit(2);
        }
        Job job = Job.getInstance(conf, "multiple tables join");
        job.setJarByClass(FactoryAddress.class);
        job.setMapperClass(FactoryAddressMapper.class);
        job.setReducerClass(FactoryAddressReducer.class);
        job.setMapOutputKeyClass(IntWritable.class);
        job.setMapOutputValueClass(Text.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        for (int i = 0; i < otherArgs.length - 1; ++i) {
            FileInputFormat.addInputPath(job, new Path(otherArgs[i]));
        }
        FileOutputFormat.setOutputPath(job, new Path(otherArgs[otherArgs.length - 1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }

}

```
