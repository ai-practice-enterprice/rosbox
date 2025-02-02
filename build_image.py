from jinja2 import Environment, FileSystemLoader
import os
import argparse

# defines
base_templates_path = 'base_templates'
ros_templates_path = 'ros_templates'
entrypoints_templates_path = 'entrypoints_templates'

class DockerfileGenerator:
    def __init__(self):
        self.base_templates = self.load_base_templates_options()
        self.ros_templates = self.load_ros_templates_options()
        self.entrypoints_templates = self.load_entrypoints_templates_options()

    def load_base_templates_options(self):
        template_files = {}
        for filename in os.listdir(base_templates_path):
            if filename.endswith('.jinja'):
                key = filename.replace('.jinja', '')
                key = key.replace('Dockerfile.', '')
                template_files[key] = os.path.join(base_templates_path, filename)
        return template_files
    
    def load_ros_templates_options(self):
        template_files = {}
        for filename in os.listdir(ros_templates_path):
            if filename.endswith('.template'):
                key = filename.replace('.template', '')
                key = key.replace('Dockerfile.', '')
                template_files[key] = os.path.join(ros_templates_path, filename)
        return template_files
    
    def load_entrypoints_templates_options(self):
        template_files = {}
        for filename in os.listdir(entrypoints_templates_path):
            if filename.endswith('.template'):
                key = filename.replace('.template', '')
                key = key.replace('Dockerfile.', '')
                template_files[key] = os.path.join(entrypoints_templates_path, filename)
        return template_files
    
    def generate_dockerfile(self, base_template, ros_template, entrypoint_template, output_file):
        ros_template = self.ros_templates[ros_template]
        base_template = self.base_templates[base_template]
        entrypoint_template = self.entrypoints_templates[entrypoint_template]
        
        # Read the ROS install Dockerfile template from its file
        with open(ros_template, 'r') as file:
            ros_dockerfile_template = file.read()
        
        # Read the entrypoint Dockerfile template from its file
        with open(entrypoint_template, 'r') as file:
            entrypoint_template_str = file.read()
        
        # Define the context mapping that will be used to render the base template
        context = {
            'ros_install': ros_dockerfile_template,
            'entrypoint_setup': entrypoint_template_str
        }
        
        # Render the base template with the provided context data
        with open(base_template, 'r') as file:
            base_template_str = file.read()
        env = Environment()
        template_obj = env.from_string(base_template_str)
        rendered_dockerfile = template_obj.render(context)
        
        # Write the rendered content to the specified output file
        with open(output_file, 'w') as f:
            f.write(rendered_dockerfile)

def main():
    # Create a Dockerfile generator
    generator = DockerfileGenerator()

    # Setup the main parser with an overview of available template options
    parser = argparse.ArgumentParser(
        description='Dockerfile Generator\n'
                    'Available base templates: ' + ', '.join(generator.base_templates.keys()) + '\n'
                    'Available ROS templates: ' + ', '.join(generator.ros_templates.keys()) + '\n'
                    'Available entrypoints templates: ' + ', '.join(generator.entrypoints_templates.keys())
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Sub-command to execute')

    # Subparser for the "gen" command with detailed arguments and choices
    gen_parser = subparsers.add_parser('gen', help='Generate a Dockerfile using specified templates')
    gen_parser.add_argument('--base', required=True, choices=list(generator.base_templates.keys()),
                            help='Base template to use. Options: ' + ', '.join(generator.base_templates.keys()))
    gen_parser.add_argument('--ros', required=True, choices=list(generator.ros_templates.keys()),
                            help='ROS variant template to use. Options: ' + ', '.join(generator.ros_templates.keys()))
    gen_parser.add_argument('--entrypoint', required=True, choices=list(generator.entrypoints_templates.keys()),
                            help='Entrypoint template to use. Options: ' + ', '.join(generator.entrypoints_templates.keys()))

    # Subparser for the "build" command
    build_parser = subparsers.add_parser('build', help='Build the Docker image')
    build_parser.add_argument('--image', required=True, help='Name of the image to build')
    
    args = parser.parse_args()
    
    if args.command == 'gen':
        # Use the selected templates for generation
        print("Selected Base Template:", args.base)
        print("Selected ROS Template:", args.ros)
        print("Selected Entrypoint Template:", args.entrypoint)

        # Generation logic here
        generator.generate_dockerfile(args.base, args.ros, args.entrypoint, 'Dockerfile')

    elif args.command == 'build':
        dockerfile_path = 'Dockerfile'
        if os.path.exists(dockerfile_path):
            os.system(f'docker build -t {args.image} .')
        else:
            print("Error: Dockerfile not found. Please generate the Dockerfile first!")


if __name__ == '__main__':
    main()