# Generate or translate your presentation with Amazon Bedrock!

This application generates professional PowerPoint presentations using Amazon Bedrock ConverseAPI and tool calling. It takes a topic from the user and automatically creates a structured presentation with customizable slides, images, and formatting.

## Features

- Generate complete presentations from a simple topic description
- Customize contact information and company details
- Generate background images and slide images using Amazon Nova Canvas
- Support for multiple slide layouts and formats
- Automatic generation of agenda and thank you slides
- Slide thumbnails preview rendering via OpenOffice integration
- Cost estimation for token usage and image generation

## Technical Implementation

The application uses:

- Amazon Bedrock's Claude models (3.5 Haiku, 3.5 Sonnet, 3.7, 4 Sonnet) and Amazon Nova models (Pro or Lite) for text generation
- Amazon Nova Canvas for creating custom images
- [python-pptx](https://pypi.org/project/python-pptx/) for PowerPoint file manipulation
- [Streamlit](https://pypi.org/project/streamlit/) for the user interface

## Recent Updates

The application has been refactored to use a more efficient approach for generating slide content. Instead of using invoke_model, now it leverage the Bedrock Converse API with function calling to generate well-formatted JSON responses.

This approach:
1. Provides better control over the output format
2. Ensures consistent slide generation
3. Maintains compatibility with all Claude and Amazon Nova models
4. Improves error handling and validation

## Usage

1. Enter your presentation topic
2. Select the number of slides
3. Choose whether to include agenda and thank you slides
4. Optionally generate custom background and slide images
5. Customize your contact information
6. Click "Generate presentation" to create your PowerPoint file
7. Download the generated presentation

### Look and feel

- Frontend page:
<img src="./tmp/generate-your-presentation-with-llm.png">

- Output example
<img src="./tmp/generate-your-presentation-with-llm-example.png">


## Installation

### Requirements

- Python 3.8+
- AWS credentials with access to Amazon Bedrock
- Required Python packages (see pyproject.toml)

### Infrastructure setup via EC2

- Pick a region, e.g. `us-east-1`

- [Launch an EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance-wizard.html#liw-quickly-launch-instance) with Amazon Linux OS with a Key pair for login (t2.medium is enough, increase the disk size to 50GB)
    - Ensure that the associated EBS volume is encrypted, as suggested in the [Configure storage section](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance-wizard.html#liw-quickly-launch-instance)
    - Enable [termination protection](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Using_ChangingDisableAPITermination.html) to protect the instance from being accidentally terminated
    - Activate an operating system patching and maintenance system like the [patch manager of AWS Systems Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager.html)

- Create a [IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_job-functions_create-policies.html) allowing access to the required models in Amazon Bedrock, e.g. defining the following [inline policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_job-functions_create-policies.html)
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "pptxBedrockAllow",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": ["arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                        "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-3-5-haiku-20241022-v1:0",
                        "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-3-7-sonnet-20250106-v1:0",
                        "arn:aws:bedrock:us-east-1::foundation-model/us.anthropic.claude-4-sonnet-20250106-v1:0",
                        "arn:aws:bedrock:us-east-1::foundation-model/us.amazon.nova-pro-v1:0",
                        "arn:aws:bedrock:us-east-1::foundation-model/us.amazon.nova-lite-v1:0",
                        "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-canvas-v1:0"]
        }
    ]
}
```
and [attach it to the EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html#attach-iam-role).

- Enable the Claude 3.5, Claude 3.7, Claude 4 Sonnet and Amazon Nova models in the [Amazon Bedrock console](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
    - Consider enabling [model invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) and set alerts to ensure adherence to any responsible AI policies.	Model invocation logging is disabled by default.


- Enable encryption in transit and allow traffic only through the Load Balancer
    - Launch an [Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancer-getting-started.html) with a dedicated Security group opened to receive traffic from the internet
    - Add an [HTTPS listener](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html) on the port `8001` of the Load Balancer which will be used to launch the application (change it accordingly if another port is used below), pointing to the target group containing the EC2 instance
    - Open the port `8001` of the EC2 Security Group port to accept traffic from the Load Balancer Security Group

### Application setup

- [Login into the EC2 via SSH](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html) and update the system packages 
```
sudo yum update
```

- Install git: 
```
sudo yum install -y git
```

- Register git credentials (change name and email!)
```
git config --global user.name "My First and Last Name"
```
```
git config --global user.email "myname@myemail.com"
```

- Install OpenOffice to be able to render the slides thumbnails (cfr [these instructions](https://www.javatpoint.com/how-to-install-apache-openoffice-on-centos))
    - **NB** if OpenOffice is not installed, no error will be thrown by the frontend but no thumbnails will be generated
```
wget https://master.dl.sourceforge.net/project/openofficeorg.mirror/4.1.5/binaries/en-GB/Apache_OpenOffice_4.1.5_Linux_x86-64_install-rpm_en-GB.tar.gz?viasf=1
tar xvf Apache_OpenOffice_4.1.5_Linux_x86-64_install-rpm_en-GB.tar.gz
cd en-GB/RPMS/
sudo rpm -Uvh *.rpm
cd ~/
```

- Install other  dependencies required by OpenOffice
```
sudo yum install -y libXrender.x86_64
sudo yum install -y libXtst.x86_64
sudo yum install -y libxcrypt-compat
sudo yum install -y libXext.x86_64
sudo yum install -y xorg-x11-server-Xvfb
```

- Install the python virtual environment manager `poetry` as per [these instructions](https://www.digitalocean.com/community/tutorials/how-to-install-poetry-to-manage-python-dependencies-on-ubuntu-22-04)
```
curl -sSL https://install.python-poetry.org | python3 -
```

- Clone the repository
```
git clone https://github.com/aws-samples/generate-your-presentation-with-llm.git
```


- Enter in the repository folder 
```
cd generate-your-presentation-with-llm
```

- Install the repository python dependencies with 
```
poetry lock
poetry install
```

- Activate the environment with 
```
poetry shell
```

- Start a `screen` terminal to be able to run a detached session after logout ([more info about screen here](https://www.geeksforgeeks.org/screen-command-in-linux-with-examples/))

```
screen
```

- insert your preferred password in the [secrets.toml](.streamlit/secrets.toml) file, replacing the *unquoted* string `YOUR_SECRET_PASSWORD`. The application will throw an exception of kind `toml.decoder.TomlDecodeError: This float doesn't have a leading digit` and will not start if this string is not replaced

- launch the application within the `screen` terminal
```
streamlit run pptx-generator.py --server.enableCORS true --server.port 8001 --browser.serverPort 8001
```

- To exit out the `screen` without interrupting the session use the keyboard combination `Ctrl+a+d`, to connect again to the session use the command `screen -r`


- login to the public page with the provided credentials (default is user: `admin`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
