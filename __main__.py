import league2
import os
import sandbox

if __name__ == '__main__':
    league2.init()

    settings = league2.Settings()
    settings.set_buffer_size(sandbox.GAME_SIZE)
    settings.set_size(sandbox.GAME_SIZE)
    settings.set_asset_folder(os.path.join(league2.get_executing_path(__file__), 'assets'))

    league2.run(sandbox.SandboxGame, settings)
    league2.quit()
