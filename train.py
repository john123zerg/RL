import gymnasium as gym
from stable_baselines3 import SAC, TD3, A2C,PPO,DDPG
import os
import argparse
import re
import numpy as np
from sb3_contrib import TRPO
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise




# Create directories to hold models and logs
model_dir = "models"
log_dir = "logs"
os.makedirs(model_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)
        # 정규 표현식을 사용하여 가장 안쪽에 있는 <와 > 사이의 모든 문자를 찾아 제거
pattern = re.compile(r'<([^<>]*)>')


def train(env, sb3_algo,policy):
    #policy_='MlpPolicy','CnnPolicy',MultiInputPolicy',
    # The noise objects for DDPG
    n_actions = env.action_space.shape[-1]
    action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
    match sb3_algo:
        case 'SAC':
            model = SAC(policy, env, action_noise=action_noise,verbose=1, device='cuda', tensorboard_log=log_dir)
        case 'TD3':
            model = TD3(policy, env,action_noise=action_noise, verbose=1, device='cuda', tensorboard_log=log_dir)
        case 'A2C':
            model = A2C(policy, env, action_noise=action_noise,verbose=1, device='cuda', tensorboard_log=log_dir)
        case 'TRPO':
            model = TRPO(policy, env,verbose=1, device='cuda', tensorboard_log=log_dir)
        case 'PPO':
            model = PPO(policy, env, action_noise=action_noise,verbose=1, device='cuda', tensorboard_log=log_dir)
        case 'DDPG':
            model = DDPG(policy, env, action_noise=action_noise,verbose=1, device='cuda', tensorboard_log=log_dir)
        case _:
            print('Algorithm not found')
            return

    TIMESTEPS = 25000
    iters = 0
    while True:
        iters += 1
        modified_file_name = re.search(pattern, str(env))

        if modified_file_name:
            inner_content = modified_file_name.group(1)
            print(inner_content)
        model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)
        file_name=f"{model_dir}/{inner_content}_{sb3_algo}_{policy}_{TIMESTEPS*iters}"
        model.save(file_name)

def test(env, sb3_algo, path_to_model):

    match sb3_algo:
        case 'SAC':
            model = SAC.load(path_to_model, env=env)
        case 'TD3':
            model = TD3.load(path_to_model, env=env)
        case 'A2C':
            model = A2C.load(path_to_model, env=env)
        case 'PPO':
            model = PPO.load(path_to_model, env=env)
        case 'TRPO':
            model = TRPO.load(path_to_model, env=env)
        case 'DDPG':
            model = DDPG.load(path_to_model, env=env)
        case _:
            print('Algorithm not found')
            return

    obs = env.reset()[0]
    done = False
    extra_steps = 500
    while True:
        action, _states = model.predict(obs)
        obs, _, done, _, _ = env.step(action)

        if done:
            extra_steps -= 1

            if extra_steps < 0:
                break


if __name__ == '__main__':

    # Parse command line inputs
    parser = argparse.ArgumentParser(description='Train or test model.')
    parser.add_argument('gymenv', help='Gymnasium environment i.e. Humanoid-v4')
    parser.add_argument('sb3_algo', help='StableBaseline3 RL algorithm i.e. SAC, TD3')
    parser.add_argument('-t', '--train', action='store_true')
    parser.add_argument('-s', '--test', metavar='path_to_model')
    parser.add_argument('-p','--policy')
    args = parser.parse_args()


    if args.train:
        gymenv = gym.make(args.gymenv, render_mode=None)
        train(gymenv, args.sb3_algo,args.policy)

    if(args.test):
        if os.path.isfile(args.test):
            gymenv = gym.make(args.gymenv, render_mode='human')
            test(gymenv, args.sb3_algo, path_to_model=args.test)
        else:
            print(f'{args.test} not found.')
